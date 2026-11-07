"""Tests for task-set loading, task resolution and test snapshots."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from evaluation.common.paths import default_tasks_root, repo_root
from evaluation.common.tasks import (
    load_task_set,
    modified_test_files,
    resolve_task_dir,
    resolve_task_set,
    snapshot_test_files,
    task_dataset_id,
)


class TaskSetTest(unittest.TestCase):
    def test_example_set(self) -> None:
        spec = load_task_set(repo_root() / "data" / "task_set" / "example.yaml")
        self.assertEqual(spec.name, "example")
        self.assertEqual(spec.random_seed, 42)
        self.assertEqual(len(spec.task_paths), 8)
        self.assertEqual(spec.task_paths[0], "coding/easy/0001")

    def test_minimal_set(self) -> None:
        spec = load_task_set(repo_root() / "data" / "task_set" / "minimal.yaml")
        self.assertEqual(spec.task_paths, ("coding/easy/0001", "data_analysis/easy/0001"))

    def test_inline_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "set.yaml"
            path.write_text(
                "dataset:\n  random_seed: 7\n  tasks: [a/b/1, c/d/2]\n",
                encoding="utf-8",
            )
            spec = load_task_set(path)
        self.assertEqual(spec.random_seed, 7)
        self.assertEqual(spec.task_paths, ("a/b/1", "c/d/2"))

    def test_json_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "set.json"
            path.write_text(
                json.dumps({"dataset": {"random_seed": 1, "tasks": ["x/y/z"]}}),
                encoding="utf-8",
            )
            spec = load_task_set(path)
        self.assertEqual(spec.task_paths, ("x/y/z",))

    def test_empty_tasks_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "set.yaml"
            path.write_text("dataset:\n  tasks: []\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_task_set(path)

    def test_resolve_example_tasks(self) -> None:
        spec = load_task_set(repo_root() / "data" / "task_set" / "example.yaml")
        tasks = resolve_task_set(spec, default_tasks_root())
        self.assertEqual(len(tasks), 8)
        self.assertEqual(tasks[0].task_id, "coding_0003")
        self.assertEqual(tasks[0].reward, 2.0)

    def test_dataset_id_is_the_task_path(self) -> None:
        task = resolve_task_set(
            load_task_set(repo_root() / "data" / "task_set" / "minimal.yaml"),
            default_tasks_root(),
        )[0]
        self.assertEqual(task.task_id, "coding_0003")
        self.assertEqual(task_dataset_id(task), "coding/easy/0001")


class ResolveTaskDirTest(unittest.TestCase):
    def test_relative_path(self) -> None:
        path = resolve_task_dir("coding/easy/0001", default_tasks_root())
        self.assertTrue((path / "task.json").is_file())

    def test_task_id(self) -> None:
        path = resolve_task_dir("data_analysis_0002", default_tasks_root())
        self.assertEqual(path.name, "0001")
        payload = json.loads((path / "task.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["task_id"], "data_analysis_0002")

    def test_missing_task(self) -> None:
        with self.assertRaises(FileNotFoundError):
            resolve_task_dir("no/such/task", default_tasks_root())


class TestSnapshotTest(unittest.TestCase):
    def test_detects_change_and_removal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            test_file = workspace / "test_a.py"
            test_file.write_text("def test_ok():\n    pass\n", encoding="utf-8")
            snapshot = snapshot_test_files(workspace)
            self.assertEqual(modified_test_files(workspace, snapshot), [])

            test_file.write_text("def test_ok():\n    assert False\n", encoding="utf-8")
            self.assertEqual(modified_test_files(workspace, snapshot), ["test_a.py"])

            test_file.unlink()
            self.assertEqual(modified_test_files(workspace, snapshot), ["test_a.py"])

    def test_detects_added_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            snapshot = snapshot_test_files(workspace)
            (workspace / "test_new.py").write_text("pass\n", encoding="utf-8")
            self.assertEqual(modified_test_files(workspace, snapshot), ["test_new.py"])


if __name__ == "__main__":
    unittest.main()
