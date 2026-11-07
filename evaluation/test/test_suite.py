"""Tests for the suite preparation/evaluation pipeline (without an LLM)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from evaluation.common.suite import (
    evaluate_suite,
    prepare_suite,
    summarize,
)
from evaluation.common.tasks import load_task


def make_task(
    base: Path,
    *,
    task_id: str,
    check: str,
    expected: str,
    reward: int = 1,
    files: dict[str, str] | None = None,
):
    root = base / task_id
    root.mkdir(parents=True)
    (root / "task.json").write_text(
        json.dumps(
            {
                "task_id": task_id,
                "task_type": "test",
                "instruction": "test",
                "reward": reward,
                "expected": expected,
                "check": check,
            }
        ),
        encoding="utf-8",
    )
    for relative, content in (files or {}).items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return load_task(root)


class SuiteTest(unittest.TestCase):
    TEST = (
        "import unittest\n"
        "import mylib\n"
        "\n"
        "class T(unittest.TestCase):\n"
        "    def test_add(self):\n"
        "        self.assertEqual(mylib.add(1, 2), 3)\n"
        "\n"
        "if __name__ == '__main__':\n"
        "    unittest.main()\n"
    )

    def _tasks(self, base: Path):
        math_task = make_task(
            base,
            task_id="math_1",
            check="exact_int",
            expected="7",
            reward=3,
        )
        # A stale answer from a previous local run must be removed by prepare_suite.
        (math_task.root / "answer.txt").write_text("999\n", encoding="utf-8")

        coding_task = make_task(
            base,
            task_id="coding_1",
            check="unittest",
            expected="tests_pass",
            reward=2,
            files={
                "workspace/mylib.py": "def add(a, b):\n    return a - b\n",
                "workspace/test_mylib.py": self.TEST,
            },
        )
        return [math_task, coding_task]

    def test_prepare_removes_stale_answers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            tasks = self._tasks(base / "source")
            prepared = prepare_suite(tasks, base / "work")
            copied_math = prepared.copied["math_1"]
            self.assertFalse((copied_math.root / "answer.txt").exists())
            self.assertTrue((copied_math.root / "task.json").is_file())

    def test_evaluate_suite_scores_and_detects_edits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            tasks = self._tasks(base / "source")
            prepared = prepare_suite(tasks, base / "work")

            math_copy = prepared.copied["math_1"]
            (math_copy.root / "answer.txt").write_text("7\n", encoding="utf-8")
            coding_copy = prepared.copied["coding_1"]
            (coding_copy.workspace / "mylib.py").write_text(
                "def add(a, b):\n    return a + b\n",
                encoding="utf-8",
            )
            (coding_copy.workspace / "answer.txt").write_text(
                "DONE\n",
                encoding="utf-8",
            )

            solutions = {
                "math_1": {
                    "answer": "7",
                    "input_tokens": 100,
                    "output_tokens": 20,
                    "cost": 30,
                },
                "coding_1": {
                    "answer": "DONE",
                    "input_tokens": 50,
                    "output_tokens": 10,
                    "cost": 15,
                },
            }
            outcomes = evaluate_suite(
                prepared,
                solutions,
                python=sys.executable,
            )
            summary = summarize(outcomes)
            self.assertEqual(summary.score, 5)
            self.assertEqual(summary.max_score, 5)
            self.assertEqual(summary.solved_tasks, 2)
            self.assertEqual(summary.cost, 45)
            self.assertEqual(outcomes[0].verdict.solved, True)
            self.assertEqual(outcomes[1].verdict.solved, True)

            # Editing the test must invalidate the coding task.
            (coding_copy.workspace / "test_mylib.py").write_text(
                "import unittest\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n",
                encoding="utf-8",
            )
            outcomes = evaluate_suite(prepared, solutions, python=sys.executable)
            summary = summarize(outcomes)
            self.assertEqual(summary.score, 3)
            self.assertFalse(outcomes[1].verdict.solved)
            self.assertEqual(outcomes[1].test_files_modified, ["test_mylib.py"])

    def test_duplicate_task_ids_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            first = make_task(
                base / "a", task_id="same", check="exact_int", expected="1"
            )
            second = make_task(
                base / "b", task_id="same", check="exact_int", expected="1"
            )
            with self.assertRaises(ValueError):
                prepare_suite([first, second], base / "work")


if __name__ == "__main__":
    unittest.main()
