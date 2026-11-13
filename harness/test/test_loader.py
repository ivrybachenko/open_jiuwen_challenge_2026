"""Task discovery must survive a hidden set with unexpected formatting."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from harness.tasks import Task, load_tasks


def _write(root: Path, name: str, payload, *, raw: bytes | None = None) -> Path:
    task_dir = root / name
    task_dir.mkdir(parents=True, exist_ok=True)
    path = task_dir / "task.json"
    if raw is not None:
        path.write_bytes(raw)
    else:
        path.write_text(json.dumps(payload), encoding="utf-8")
    return task_dir


class LoaderTest(unittest.TestCase):
    def test_reads_utf8_bom(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root,
                "bom",
                None,
                raw=b'\xef\xbb\xbf{"task_id": "bom", '
                b'"task_type": "math", "instruction": "x", "reward": 2}',
            )
            tasks = load_tasks(root)
        self.assertEqual([task.task_id for task in tasks], ["bom"])
        self.assertEqual(tasks[0].reward, 2.0)

    def test_invalid_reward_does_not_stop_loading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "good", {"task_id": "good", "instruction": "x", "reward": 3})
            _write(root, "bad", {"task_id": "bad", "instruction": "x", "reward": "N/A"})
            _write(root, "string", {"task_id": "string", "instruction": "x", "reward": "7"})
            with self.assertLogs("harness.tasks.loader", level="WARNING"):
                tasks = load_tasks(root)
        by_id = {task.task_id: task for task in tasks}
        self.assertEqual(set(by_id), {"good", "bad", "string"})
        self.assertEqual(by_id["good"].reward, 3.0)
        self.assertEqual(by_id["bad"].reward, 0.0)
        self.assertEqual(by_id["string"].reward, 7.0)

    def test_non_object_payload_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "good", {"task_id": "good", "instruction": "x", "reward": 1})
            _write(root, "list", None, raw=b"[1, 2, 3]")
            _write(root, "string", None, raw=b'"not an object"')
            with self.assertLogs("harness.tasks.loader", level="WARNING"):
                tasks = load_tasks(root)
        self.assertEqual([task.task_id for task in tasks], ["good"])

    def test_non_finite_and_negative_reward_is_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, reward in (
                ("nan", "NaN"),
                ("inf", "Infinity"),
                ("negative", -5),
                ("null", None),
            ):
                _write(root, name, {"task_id": name, "instruction": "x", "reward": reward})
            with self.assertLogs("harness.tasks.loader", level="WARNING"):
                tasks = load_tasks(root)
        self.assertEqual({task.task_id: task.reward for task in tasks}, {
            "nan": 0.0,
            "inf": 0.0,
            "negative": 0.0,
            "null": 0.0,
        })

    def test_missing_fields_get_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "folder", {"instruction": "x"})
            tasks = load_tasks(root)
        self.assertEqual(tasks[0].task_id, "folder")
        self.assertEqual(tasks[0].task_type, "unknown")
        self.assertEqual(tasks[0].reward, 0.0)

    def test_duplicate_task_id_warns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "first", {"task_id": "same", "instruction": "x", "reward": 1})
            _write(root, "second", {"task_id": "same", "instruction": "y", "reward": 2})
            with self.assertLogs("harness.tasks.loader", level="WARNING") as logs:
                tasks = load_tasks(root)
        self.assertEqual(len(tasks), 2)
        self.assertIn("duplicate task_id", "\n".join(logs.output))

    def test_dataset_flags_are_not_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root,
                "impossible",
                {
                    "task_id": "impossible",
                    "instruction": "x",
                    "reward": 4,
                    "solvable": False,
                    "impossible": True,
                },
            )
            tasks = load_tasks(root)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].reward, 4.0)

    def test_task_json_symlink_outside_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = Path(tmp) / "outside.json"
            outside.write_text(
                json.dumps({"task_id": "leak", "instruction": "x", "reward": 1}),
                encoding="utf-8",
            )
            task_dir = root / "leak"
            task_dir.mkdir()
            (task_dir / "task.json").symlink_to(outside)
            with self.assertLogs("harness.tasks.loader", level="WARNING"):
                tasks = load_tasks(root)
        self.assertEqual(tasks, [])


class TaskPathTest(unittest.TestCase):
    def test_workspace_symlink_outside_the_task_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "tasks" / "task"
            root.mkdir(parents=True)
            outside = Path(tmp) / "outside"
            outside.mkdir()
            os.symlink(outside, root / "workspace")
            (root / "task.json").write_text(
                json.dumps({"task_id": "task", "instruction": "x", "reward": 1}),
                encoding="utf-8",
            )
            task = load_tasks(root.parent)[0]
            self.assertEqual(task.workspace, root)
            self.assertEqual(task.answer_paths, (root / "answer.txt",))

    def test_answer_symlink_outside_the_task_is_not_read_or_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "tasks" / "task"
            workspace = root / "workspace"
            workspace.mkdir(parents=True)
            outside = Path(tmp) / "outside.txt"
            outside.write_text("secret", encoding="utf-8")
            os.symlink(outside, workspace / "answer.txt")
            os.symlink(outside, root / "answer.txt")
            task = Task(
                task_id="task",
                task_type="math",
                instruction="x",
                reward=1.0,
                expected=None,
                check=None,
                root=root,
            )
            self.assertIsNone(task.read_answer())
            with self.assertLogs("harness.tasks.model", level="WARNING"):
                with self.assertRaises(OSError):
                    task.write_answer("42")
            self.assertEqual(outside.read_text(encoding="utf-8"), "secret")

    def test_answer_inside_the_task_is_written_to_both_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "tasks" / "task"
            (root / "workspace").mkdir(parents=True)
            task = Task(
                task_id="task",
                task_type="math",
                instruction="x",
                reward=1.0,
                expected=None,
                check=None,
                root=root,
            )
            task.write_answer("42")
            self.assertEqual(
                (root / "workspace" / "answer.txt").read_text().strip(), "42"
            )
            self.assertEqual((root / "answer.txt").read_text().strip(), "42")
            self.assertEqual(task.read_answer(), "42\n")


if __name__ == "__main__":
    unittest.main()
