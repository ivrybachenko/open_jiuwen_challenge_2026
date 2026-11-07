"""Tests for the Docker checker using a fake ``docker`` executable."""

from __future__ import annotations

import json
import os
import stat
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from evaluation.dockerfile_checker.checker import check_dockerfile


FAKE_DOCKER = textwrap.dedent(
    """\
    #!/usr/bin/env python3
    import json
    import sys
    from pathlib import Path

    args = sys.argv[1:]
    if not args:
        sys.exit(0)

    if args[0] == "build":
        print("fake build ok")
        sys.exit(0)

    if args[0] == "image" and len(args) >= 2 and args[1] == "inspect":
        # Compressed size: the checker must prefer `docker images` instead.
        print(999999)
        sys.exit(0)

    if args[0] == "images":
        print("123456B")
        sys.exit(0)

    if args[0] == "rm":
        sys.exit(0)

    if args[0] != "run":
        sys.exit(0)

    mounts = {}
    for index, value in enumerate(args):
        if value == "-v" and index + 1 < len(args):
            spec = args[index + 1]
            host, container, *_ = spec.split(":")
            mounts[container] = Path(host)

    tasks_dir = mounts["/data/tasks"]
    out_dir = mounts["/data/out"]
    out_dir.mkdir(parents=True, exist_ok=True)

    solutions = {}
    for task_dir in sorted(tasks_dir.iterdir()):
        task_json = task_dir / "task.json"
        if not task_json.is_file():
            continue
        payload = json.loads(task_json.read_text(encoding="utf-8"))
        task_id = payload["task_id"]
        answer = "42"
        (task_dir / "answer.txt").write_text(answer + "\\n", encoding="utf-8")
        workspace = task_dir / "workspace"
        if workspace.is_dir():
            (workspace / "answer.txt").write_text(answer + "\\n", encoding="utf-8")
        solutions[task_id] = {
            "task_id": task_id,
            "reward": payload.get("reward", 0),
            "solved": True,
            "answer": answer,
            "input_tokens": 100,
            "output_tokens": 20,
            "cost": 30,
            "note": "fake docker",
            "updated_at": "",
        }

    (out_dir / "solutions.json").write_text(
        json.dumps({"solutions": solutions}), encoding="utf-8"
    )
    """
)


class DockerfileCheckerTest(unittest.TestCase):
    def _make_repo(self, base: Path) -> Path:
        repo = base / "repo"
        task = repo / "data" / "task" / "math" / "1"
        task.mkdir(parents=True)
        (task / "task.json").write_text(
            json.dumps(
                {
                    "task_id": "math_1",
                    "task_type": "math",
                    "instruction": "test",
                    "reward": 2,
                    "expected": "42",
                    "check": "exact_int",
                }
            ),
            encoding="utf-8",
        )
        task_set = repo / "data" / "task_set" / "minimal.yaml"
        task_set.parent.mkdir(parents=True)
        task_set.write_text(
            "dataset:\n  random_seed: 1\n  tasks:\n    - math/1\n",
            encoding="utf-8",
        )
        (repo / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
        return repo

    def test_build_size_and_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = self._make_repo(base)
            docker_bin = base / "bin"
            docker_bin.mkdir()
            fake_docker = docker_bin / "docker"
            fake_docker.write_text(FAKE_DOCKER, encoding="utf-8")
            fake_docker.chmod(fake_docker.stat().st_mode | stat.S_IEXEC)

            env = dict(os.environ)
            env["PATH"] = str(docker_bin) + os.pathsep + env.get("PATH", "")
            env["LLM_BASE_URL"] = "http://fake"
            env["LLM_API_KEY"] = "fake"
            with mock.patch.dict(os.environ, env, clear=False):
                report = check_dockerfile(
                    repo=repo,
                    image="fake:latest",
                    task_set_path=repo / "data" / "task_set" / "minimal.yaml",
                    tasks_root=repo / "data" / "task",
                    cpus="6",
                    python=sys.executable,
                    build_timeout=30.0,
                    run_timeout=30.0,
                )

            self.assertIsNotNone(report.build)
            self.assertTrue(report.build.ok)
            self.assertEqual(report.image_size_bytes, 123456)
            self.assertEqual(report.cpus, "6")
            self.assertIsNotNone(report.run)
            self.assertTrue(report.run.ok)
            self.assertIsNotNone(report.summary)
            self.assertEqual(report.summary.score, 2)
            self.assertEqual(report.summary.max_score, 2)
            self.assertEqual(report.summary.cost, 30)
            self.assertIsNone(report.work_dir)


if __name__ == "__main__":
    unittest.main()
