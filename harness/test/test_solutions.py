"""Unit tests for the solutions file and its fallback paths."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from harness.application.solutions import Solution, SolutionsStore


def make_solution(task_id: str = "math_0000", reward: float = 5.0) -> Solution:
    return Solution(
        task_id=task_id,
        reward=reward,
        solved=True,
        answer="42",
        input_tokens=10,
        output_tokens=5,
        cost=6,
        note="answer_kind=value; attempts=1",
        updated_at="2026-01-01T00:00:00+00:00",
    )


def blocked_path(root: Path, name: str = "out") -> Path:
    """A path whose parent is a regular file, so mkdir cannot succeed."""
    blocker = root / name
    blocker.write_text("not a directory\n", encoding="utf-8")
    return blocker / "solutions.json"


class SolutionsFallbackTest(unittest.TestCase):
    def test_unwritable_primary_uses_the_tasks_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            primary = blocked_path(root)
            fallback = root / "tasks" / "solutions.json"
            store = SolutionsStore(primary, fallbacks=(fallback,))

            store.record(make_solution())

            self.assertEqual(store.path, fallback)
            payload = json.loads(fallback.read_text(encoding="utf-8"))
            self.assertIn("math_0000", payload["solutions"])
            self.assertEqual(payload["total_score"], 5.0)

            store.record(make_solution("math_0001", 2.0))
            payload = json.loads(fallback.read_text(encoding="utf-8"))
            self.assertIn("math_0001", payload["solutions"])
            self.assertEqual(payload["total_score"], 7.0)

    def test_no_writable_path_does_not_raise(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            primary = blocked_path(root, "a")
            fallback = blocked_path(root, "b")
            store = SolutionsStore(primary, fallbacks=(fallback,))

            store.record(make_solution())  # must not raise

            self.assertEqual(store.path, primary)
            self.assertFalse(primary.exists())
            self.assertFalse(fallback.exists())

    def test_resume_from_fallback_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            primary = blocked_path(root)
            fallback = root / "tasks" / "solutions.json"
            fallback.parent.mkdir(parents=True)
            fallback.write_text(
                json.dumps(
                    {
                        "total_score": 5.0,
                        "solutions": {
                            "math_0000": {
                                "reward": 5.0,
                                "solved": True,
                                "cost": 6,
                                "input_tokens": 10,
                                "output_tokens": 5,
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            store = SolutionsStore(primary, fallbacks=(fallback,))

            self.assertEqual(store.path, fallback)
            self.assertEqual(store.total_score, 5.0)
            self.assertEqual(store.total_cost, 6)

    def test_primary_path_is_preferred_when_writable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            primary = root / "out" / "solutions.json"
            fallback = root / "tasks" / "solutions.json"
            store = SolutionsStore(primary, fallbacks=(fallback,))

            store.record(make_solution())

            self.assertEqual(store.path, primary)
            self.assertTrue(primary.is_file())
            self.assertFalse(fallback.exists())


if __name__ == "__main__":
    unittest.main()
