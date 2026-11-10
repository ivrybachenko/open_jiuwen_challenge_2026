"""Smoke test for the version-committing benchmark script."""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from evaluation.commit_harness_version import main as commit_main


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


class CommitHarnessVersionTest(unittest.TestCase):
    def _make_repo(self, base: Path) -> Path:
        package = base / "harness" / "src" / "harness"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "run_agent.py").write_text(
            FAKE_RUN_AGENT + "\n",
            encoding="utf-8",
        )
        (base / "harness" / "pyproject.toml").write_text(
            '[project]\nname = "x"\nversion = "0001"\n',
            encoding="utf-8",
        )

        task = base / "data" / "task" / "test" / "solvable" / "0001"
        task.mkdir(parents=True)
        (task / "task.json").write_text(
            json.dumps(
                {
                    "task_id": "t_42",
                    "task_type": "test",
                    "instruction": "test",
                    "reward": 2,
                    "expected": "42",
                    "check": "exact_int",
                }
            ),
            encoding="utf-8",
        )

        info = base / "data" / "harness_info" / "harness_info.tsv"
        info.parent.mkdir(parents=True)
        info.write_text(
            "harness_version\tparent_harness_version\tdescription\n"
            "0001\t0000\ttest\n",
            encoding="utf-8",
        )
        return base

    def _add_task(
        self,
        base: Path,
        relative: str,
        task_id: str,
        *,
        solvable: bool = True,
    ) -> Path:
        task = base / "data" / "task" / relative
        task.mkdir(parents=True)
        payload = {
            "task_id": task_id,
            "task_type": "test",
            "instruction": "test",
            "reward": 2,
        }
        if solvable:
            payload.update({"expected": "42", "check": "exact_int"})
        else:
            payload.update({"solvable": False, "check": "none"})
        (task / "task.json").write_text(json.dumps(payload), encoding="utf-8")
        return task

    def test_single_run_writes_row_with_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = self._make_repo(Path(tmp))
            with mock.patch.dict(os.environ, {"LLM_API_KEY": "dummy"}, clear=False):
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = commit_main(
                        [
                            "--harness-version",
                            "0001",
                            "--runs",
                            "1",
                            "--max-tasks",
                            "1",
                            "--skip-set",
                            "--repo-root",
                            str(base),
                            "--tasks-root",
                            str(base / "data" / "task"),
                            "--python",
                            sys.executable,
                        ]
                    )
            self.assertEqual(rc, 0)

            lines = (
                base
                / "data"
                / "harness_task_score"
                / "harness_v_0001.tsv"
            ).read_text(encoding="utf-8").splitlines()
            self.assertEqual(
                lines[0],
                "harness_version\trun_id\ttask_id\tis_solved_correctly\t"
                "cost_tokens\tcost_seconds",
            )
            self.assertEqual(len(lines), 2)
            fields = lines[1].split("\t")
            self.assertEqual(fields[0], "0001")
            self.assertTrue(fields[1])
            self.assertEqual(fields[2], "test/solvable/0001")
            self.assertEqual(fields[3], "true")
            self.assertEqual(fields[4], "30")

    def test_existing_dataset_rows_are_kept(self) -> None:
        header = (
            "harness_version\trun_id\ttask_id\tis_solved_correctly\t"
            "cost_tokens\tcost_seconds"
        )
        with tempfile.TemporaryDirectory() as tmp:
            base = self._make_repo(Path(tmp))
            dataset = (
                base / "data" / "harness_task_score" / "harness_v_0001.tsv"
            )
            dataset.parent.mkdir(parents=True)
            dataset.write_text(
                header + "\n0001\told-run\ttest/solvable/0001\ttrue\t111\t1.000\n",
                encoding="utf-8",
            )
            with mock.patch.dict(os.environ, {"LLM_API_KEY": "dummy"}, clear=False):
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = commit_main(
                        [
                            "--harness-version",
                            "0001",
                            "--runs",
                            "1",
                            "--max-tasks",
                            "1",
                            "--skip-set",
                            "--repo-root",
                            str(base),
                            "--tasks-root",
                            str(base / "data" / "task"),
                            "--python",
                            sys.executable,
                        ]
                    )
            self.assertEqual(rc, 0)

            rows = dataset.read_text(encoding="utf-8").splitlines()[1:]
            self.assertEqual(len(rows), 2)
            self.assertTrue(any("\told-run\t" in row for row in rows))
            self.assertTrue(
                any(
                    "\ttest/solvable/0001\t" in row and "\told-run\t" not in row
                    for row in rows
                )
            )

    def test_tasks_from_selects_tasks_and_keeps_impossible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = self._make_repo(Path(tmp))
            self._add_task(
                base, "test/impossible/0001", "t_impossible", solvable=False
            )
            self._add_task(base, "test/solvable/0002", "t_other")
            task_set = base / "data" / "task_set" / "selected.yaml"
            task_set.parent.mkdir(parents=True)
            task_set.write_text(
                "dataset:\n"
                "  random_seed: 42\n"
                "  tasks:\n"
                "    - test/impossible/0001\n",
                encoding="utf-8",
            )
            with mock.patch.dict(os.environ, {"LLM_API_KEY": "dummy"}, clear=False):
                with contextlib.redirect_stdout(io.StringIO()) as stdout:
                    rc = commit_main(
                        [
                            "--harness-version",
                            "0001",
                            "--runs",
                            "1",
                            "--skip-set",
                            "--tasks-from",
                            str(task_set),
                            "--repo-root",
                            str(base),
                            "--tasks-root",
                            str(base / "data" / "task"),
                            "--python",
                            sys.executable,
                        ]
                    )
            self.assertEqual(rc, 0)
            self.assertIn("tasks from: selected", stdout.getvalue())

            dataset = (
                base / "data" / "harness_task_score" / "harness_v_0001.tsv"
            )
            rows = dataset.read_text(encoding="utf-8").splitlines()[1:]
            self.assertEqual(len(rows), 1)
            fields = rows[0].split("\t")
            self.assertEqual(fields[2], "test/impossible/0001")
            self.assertEqual(fields[3], "false")

    def test_max_tasks_applies_after_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = self._make_repo(Path(tmp))
            self._add_task(base, "test/solvable/0002", "t_other")
            task_set = base / "data" / "task_set" / "selected.yaml"
            task_set.parent.mkdir(parents=True)
            task_set.write_text(
                "dataset:\n"
                "  random_seed: 42\n"
                "  tasks:\n"
                "    - test/solvable/0001\n"
                "    - test/solvable/0002\n",
                encoding="utf-8",
            )
            with mock.patch.dict(os.environ, {"LLM_API_KEY": "dummy"}, clear=False):
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = commit_main(
                        [
                            "--harness-version",
                            "0001",
                            "--runs",
                            "1",
                            "--max-tasks",
                            "1",
                            "--skip-set",
                            "--tasks-from",
                            str(task_set),
                            "--repo-root",
                            str(base),
                            "--tasks-root",
                            str(base / "data" / "task"),
                            "--python",
                            sys.executable,
                        ]
                    )
            self.assertEqual(rc, 0)
            dataset = (
                base / "data" / "harness_task_score" / "harness_v_0001.tsv"
            )
            rows = dataset.read_text(encoding="utf-8").splitlines()[1:]
            self.assertEqual([row.split("\t")[2] for row in rows], ["test/solvable/0001"])

    def test_missing_harness_info_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = self._make_repo(Path(tmp))
            (base / "data" / "harness_info" / "harness_info.tsv").write_text(
                "harness_version\tparent_harness_version\tdescription\n",
                encoding="utf-8",
            )
            with mock.patch.dict(os.environ, {"LLM_API_KEY": "dummy"}, clear=False):
                with contextlib.redirect_stderr(io.StringIO()) as stderr:
                    rc = commit_main(
                        [
                            "--harness-version",
                            "0001",
                            "--runs",
                            "1",
                            "--max-tasks",
                            "1",
                            "--skip-set",
                            "--repo-root",
                            str(base),
                            "--tasks-root",
                            str(base / "data" / "task"),
                            "--python",
                            sys.executable,
                        ]
                    )
            self.assertEqual(rc, 2)
            self.assertIn("no row", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
