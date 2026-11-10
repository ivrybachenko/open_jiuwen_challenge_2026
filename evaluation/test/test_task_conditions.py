"""Dataset invariant C-06: a task condition must not reveal its difficulty."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from evaluation.common.paths import default_tasks_root

DIFFICULTY_WORD = re.compile(r"\b(easy|medium|hard|impossible)\b", re.IGNORECASE)
IMPOSSIBILITY_HINT = "impossible"


def _payloads():
    for path in sorted(default_tasks_root().rglob("task.json")):
        yield path, json.loads(path.read_text(encoding="utf-8"))


class TaskConditionsTest(unittest.TestCase):
    def test_instruction_has_no_difficulty_word(self) -> None:
        for path, payload in _payloads():
            with self.subTest(task=path):
                instruction = str(payload.get("instruction", ""))
                match = DIFFICULTY_WORD.search(instruction)
                if match:
                    self.fail(
                        f"{path}: instruction mentions difficulty {match.group(0)!r}"
                    )

    def test_impossible_task_does_not_announce_itself(self) -> None:
        for path, payload in _payloads():
            if payload.get("solvable") is False or payload.get("impossible") is True:
                with self.subTest(task=path):
                    instruction = str(payload.get("instruction", "")).lower()
                    self.assertNotIn(IMPOSSIBILITY_HINT, instruction, str(path))

    def test_every_task_has_a_workspace(self) -> None:
        for path, _ in _payloads():
            with self.subTest(task=path):
                self.assertTrue(
                    (path.parent / "workspace").is_dir(),
                    f"{path}: task.json would be the agent's working directory",
                )

    def test_task_ids_are_unique(self) -> None:
        ids = [str(payload.get("task_id", "")) for _, payload in _payloads()]
        duplicates = {value for value in ids if ids.count(value) > 1}
        self.assertEqual(duplicates, set(), f"duplicate task_id values: {duplicates}")


if __name__ == "__main__":
    unittest.main()
