"""End-to-end tests of the runner using a fake ``harness`` package."""

from __future__ import annotations

import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from evaluation.common.runner import HarnessConfig, run_harness
from evaluation.common.suite import run_suite
from evaluation.common.tasks import load_task


FAKE_RUN_AGENT = textwrap.dedent(
    """
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--model")
    parser.add_argument("--budget", type=int)
    parser.add_argument("--max-iterations", type=int)
    args, _ = parser.parse_known_args()

    solutions = {}
    for task_dir in sorted(Path(args.tasks_dir).iterdir()):
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
            "note": "fake",
            "updated_at": "",
        }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"solutions": solutions}), encoding="utf-8")
    """
).strip()


def make_fake_repo(base: Path) -> Path:
    package = base / "harness" / "src" / "harness"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "run_agent.py").write_text(FAKE_RUN_AGENT + "\n", encoding="utf-8")
    return base


def make_task(base: Path):
    root = base / "tasks" / "math_1"
    root.mkdir(parents=True)
    (root / "task.json").write_text(
        json.dumps(
            {
                "task_id": "math_1",
                "task_type": "test",
                "instruction": "test",
                "reward": 3,
                "expected": "42",
                "check": "exact_int",
            }
        ),
        encoding="utf-8",
    )
    return load_task(root)


class RunnerTest(unittest.TestCase):
    def test_fake_harness_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            fake_repo = make_fake_repo(base)
            task = make_task(base)
            config = HarnessConfig(repo_root=fake_repo, python=sys.executable)
            out = base / "out" / "solutions.json"

            run = run_harness(config, task.root.parent, out)

            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(out.is_file())
            self.assertIn("math_1", run.solutions)
            self.assertEqual(run.solutions["math_1"]["cost"], 30)

    def test_run_suite_evaluates_fake_answer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            fake_repo = make_fake_repo(base)
            task = make_task(base)
            config = HarnessConfig(repo_root=fake_repo, python=sys.executable)

            suite = run_suite(
                [task],
                config,
                python=sys.executable,
                keep=False,
            )

            self.assertEqual(len(suite.outcomes), 1)
            self.assertTrue(suite.outcomes[0].verdict.solved)
            self.assertEqual(suite.outcomes[0].cost, 30)
            self.assertIsNone(suite.work_dir)

    def test_trajectories_are_written_to_repo_data_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            fake_repo = make_fake_repo(base)
            task = make_task(base)
            config = HarnessConfig(repo_root=fake_repo, python=sys.executable)
            out = base / "out" / "solutions.json"

            run = run_harness(config, task.root.parent, out)

            self.assertIn("--trajectories-dir", run.command)
            index = run.command.index("--trajectories-dir")
            self.assertEqual(
                Path(run.command[index + 1]),
                (fake_repo / "data" / "trajectories").resolve(),
            )

    def test_trajectories_can_be_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            fake_repo = make_fake_repo(base)
            task = make_task(base)
            config = HarnessConfig(
                repo_root=fake_repo,
                python=sys.executable,
                save_trajectories=False,
            )
            out = base / "out" / "solutions.json"

            run = run_harness(config, task.root.parent, out)

            self.assertNotIn("--trajectories-dir", run.command)

    def test_run_id_is_passed_to_harness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            fake_repo = make_fake_repo(base)
            task = make_task(base)
            config = HarnessConfig(
                repo_root=fake_repo,
                python=sys.executable,
                run_id="run-123",
            )
            out = base / "out" / "solutions.json"

            run = run_harness(config, task.root.parent, out)

            self.assertIn("--run-id", run.command)
            index = run.command.index("--run-id")
            self.assertEqual(run.command[index + 1], "run-123")


if __name__ == "__main__":
    unittest.main()
