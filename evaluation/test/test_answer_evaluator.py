"""Tests for ``evaluation.answer_evaluator``."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from evaluation.answer_evaluator import evaluate_task
from evaluation.common.tasks import load_task


def make_task(
    base: Path,
    *,
    task_id: str = "t1",
    check: str = "exact_int",
    expected: str = "42",
    files: dict[str, str] | None = None,
    extra: dict | None = None,
):
    root = base / task_id
    root.mkdir(parents=True)
    payload = {
        "task_id": task_id,
        "task_type": "test",
        "instruction": "test",
        "reward": 1,
        "expected": expected,
        "check": check,
    }
    payload.update(extra or {})
    (root / "task.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )
    for relative, content in (files or {}).items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return load_task(root)


class ExactIntTest(unittest.TestCase):
    def test_exact_answer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(Path(tmp))
            (task.root / "answer.txt").write_text("42\n", encoding="utf-8")
            verdict = evaluate_task(task)
        self.assertTrue(verdict.solved)
        self.assertIn("42", verdict.detail)

    def test_wrong_answer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(Path(tmp))
            (task.root / "answer.txt").write_text("41\n", encoding="utf-8")
            verdict = evaluate_task(task)
        self.assertFalse(verdict.solved)

    def test_thousands_separator_is_not_regex_noise(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(Path(tmp), expected="1234")
            (task.root / "answer.txt").write_text("1,234\n", encoding="utf-8")
            verdict = evaluate_task(task)
        self.assertTrue(verdict.solved)

    def test_lenient_single_integer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(Path(tmp))
            (task.root / "answer.txt").write_text("The answer is 42.\n", encoding="utf-8")
            self.assertTrue(evaluate_task(task).solved)
            self.assertFalse(evaluate_task(task, strict=True).solved)

    def test_two_integers_are_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(Path(tmp))
            (task.root / "answer.txt").write_text("41 or 42\n", encoding="utf-8")
            self.assertFalse(evaluate_task(task).solved)

    def test_code_fence(self) -> None:
        for answer in ("```\n42\n```\n", "```42```\n"):
            with tempfile.TemporaryDirectory() as tmp:
                task = make_task(Path(tmp))
                (task.root / "answer.txt").write_text(answer, encoding="utf-8")
                self.assertTrue(evaluate_task(task).solved, answer)


class ExactStringTest(unittest.TestCase):
    def test_case_insensitive_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(Path(tmp), check="exact_str", expected="Osaka")
            (task.root / "answer.txt").write_text(" osaka. \n", encoding="utf-8")
            self.assertTrue(evaluate_task(task).solved)
            self.assertFalse(evaluate_task(task, strict=True).solved)

    def test_wrong_string(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(Path(tmp), check="exact_str", expected="Osaka")
            (task.root / "answer.txt").write_text("Kyoto\n", encoding="utf-8")
            self.assertFalse(evaluate_task(task).solved)


class UnittestCheckTest(unittest.TestCase):
    PASSING_LIB = "def add(a, b):\n    return a + b\n"
    FAILING_LIB = "def add(a, b):\n    return a - b\n"
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

    def test_passing_tests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(
                Path(tmp),
                check="unittest",
                expected="tests_pass",
                files={
                    "workspace/mylib.py": self.PASSING_LIB,
                    "workspace/test_mylib.py": self.TEST,
                    "workspace/answer.txt": "DONE\n",
                },
            )
            verdict = evaluate_task(task, python=sys.executable)
        self.assertTrue(verdict.solved)
        self.assertIn("passed", verdict.detail)

    def test_failing_tests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(
                Path(tmp),
                check="unittest",
                expected="tests_pass",
                files={
                    "workspace/mylib.py": self.FAILING_LIB,
                    "workspace/test_mylib.py": self.TEST,
                    "workspace/answer.txt": "DONE\n",
                },
            )
            verdict = evaluate_task(task, python=sys.executable)
        self.assertFalse(verdict.solved)
        self.assertIn("test_mylib.py", verdict.detail)

    def test_no_test_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(
                Path(tmp),
                check="unittest",
                expected="tests_pass",
                files={"workspace/answer.txt": "DONE\n"},
            )
            verdict = evaluate_task(task, python=sys.executable)
        self.assertFalse(verdict.solved)
        self.assertIn("no test", verdict.detail)

    def test_answer_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(
                Path(tmp),
                check="unittest",
                expected="tests_pass",
                files={
                    "workspace/mylib.py": self.PASSING_LIB,
                    "workspace/test_mylib.py": self.TEST,
                },
            )
            verdict = evaluate_task(task, python=sys.executable)
        self.assertFalse(verdict.solved)
        self.assertIn("no answer", verdict.detail)


class HiddenUnittestCheckTest(unittest.TestCase):
    PASSING_LIB = "def add(a, b):\n    return a + b\n"
    FAILING_LIB = "def add(a, b):\n    return a - b\n"
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

    def test_passing_hidden_tests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(
                Path(tmp),
                check="hidden_unittest",
                expected="tests_pass",
                files={
                    "workspace/mylib.py": self.PASSING_LIB,
                    "tests/test_hidden.py": self.TEST,
                },
            )
            (task.workspace / "answer.txt").write_text("DONE\n", encoding="utf-8")
            verdict = evaluate_task(task, python=sys.executable)
        self.assertTrue(verdict.solved)
        self.assertIn("hidden test", verdict.detail)

    def test_failing_hidden_tests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(
                Path(tmp),
                check="hidden_unittest",
                expected="tests_pass",
                files={
                    "workspace/mylib.py": self.FAILING_LIB,
                    "tests/test_hidden.py": self.TEST,
                },
            )
            (task.workspace / "answer.txt").write_text("DONE\n", encoding="utf-8")
            verdict = evaluate_task(task, python=sys.executable)
        self.assertFalse(verdict.solved)
        self.assertIn("test_hidden.py", verdict.detail)

    def test_hidden_tests_are_not_visible_tests(self) -> None:
        from evaluation.common.tasks import iter_test_files

        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(
                Path(tmp),
                check="hidden_unittest",
                expected="tests_pass",
                files={
                    "workspace/mylib.py": self.PASSING_LIB,
                    "tests/test_hidden.py": self.TEST,
                },
            )
            self.assertEqual(iter_test_files(task.workspace), [])
            self.assertEqual(len(iter_test_files(task.root / "tests")), 1)

    def test_no_hidden_tests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(
                Path(tmp),
                check="hidden_unittest",
                expected="tests_pass",
                files={
                    "workspace/mylib.py": self.PASSING_LIB,
                    "workspace/answer.txt": "DONE\n",
                },
            )
            verdict = evaluate_task(task, python=sys.executable)
        self.assertFalse(verdict.solved)
        self.assertIn("no hidden", verdict.detail)

    def test_answer_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(
                Path(tmp),
                check="hidden_unittest",
                expected="tests_pass",
                files={
                    "workspace/mylib.py": self.PASSING_LIB,
                    "tests/test_hidden.py": self.TEST,
                },
            )
            verdict = evaluate_task(task, python=sys.executable)
        self.assertFalse(verdict.solved)
        self.assertIn("no answer", verdict.detail)


class UnsupportedCheckTest(unittest.TestCase):
    def test_unknown_check_is_unsolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(Path(tmp), check="regex", expected=".*")
            (task.root / "answer.txt").write_text("anything", encoding="utf-8")
            verdict = evaluate_task(task)
        self.assertFalse(verdict.solved)
        self.assertIn("unsupported", verdict.detail)


class UnsolvableTaskTest(unittest.TestCase):
    def test_impossible_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(Path(tmp), extra={"impossible": True})
            (task.root / "answer.txt").write_text("42", encoding="utf-8")
            verdict = evaluate_task(task)
        self.assertFalse(verdict.solved)
        self.assertIn("unsolvable", verdict.detail)

    def test_solvable_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(Path(tmp), extra={"solvable": False})
            (task.root / "answer.txt").write_text("42", encoding="utf-8")
            verdict = evaluate_task(task)
        self.assertFalse(verdict.solved)
        self.assertIn("unsolvable", verdict.detail)


if __name__ == "__main__":
    unittest.main()
