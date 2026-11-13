"""Unit tests for turn features and the wave-2 heuristic."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from harness.tasks import classify_answer
from harness.accounting import AttemptLogger, extract_features
from harness.solving.scheduler import promise_score
from harness.solving.success_predictors.heuristic import success_probability


class AnswerClassificationTest(unittest.TestCase):
    def test_none_empty_and_value(self) -> None:
        self.assertEqual(classify_answer(None).kind, "none")
        self.assertEqual(classify_answer("  ").kind, "none")
        self.assertEqual(classify_answer("389").kind, "value")
        self.assertEqual(classify_answer("DONE").kind, "done")

    def test_impossible_first_line(self) -> None:
        info = classify_answer("IMPOSSIBLE\nThe data contradicts itself.")
        self.assertEqual(info.kind, "impossible")
        self.assertEqual(info.first_line, "IMPOSSIBLE")


class FeatureExtractionTest(unittest.TestCase):
    def test_keywords_and_limits(self) -> None:
        features = extract_features(
            task_type="math",
            reward=5,
            wave=1,
            turn=1,
            reasoning="This is impossible. I cannot determine the answer. no solution",
            model_duration_seconds=3.2,
            input_tokens=1000,
            output_tokens=999,
            reasoning_tokens=500,
            finish_reason="length",
            max_tokens=1000,
            script="python3 -c 'print(1)' > answer.txt",
            exit_code=0,
            script_duration_seconds=0.2,
            script_timed_out=False,
            script_error="",
            output_chars=12,
            answer=classify_answer("1"),
            tests_in_overview=False,
        )
        self.assertTrue(features["hit_token_limit"])
        self.assertGreater(features["reasoning_keyword_impossible"], 0)
        self.assertTrue(features["script_has_python"])
        self.assertTrue(features["script_has_write_answer"])
        self.assertEqual(features["answer_kind"], "value")

    def test_impossible_answer_is_less_promising(self) -> None:
        base = {
            "answer_kind": "none",
            "hit_token_limit": False,
            "script_error": "",
            "script_timed_out": False,
            "exit_code": 0,
            "reasoning_keyword_impossible": 0,
            "reasoning_keyword_give_up": 0,
            "reasoning_words": 100,
            "script_has_write_answer": True,
            "script_has_python": True,
            "output_chars": 100,
            "tests_in_overview": False,
        }
        impossible = dict(base, answer_kind="impossible")
        self.assertLess(
            success_probability(impossible), success_probability(base)
        )

    def test_promise_uses_reward_and_cost(self) -> None:
        features = {
            "answer_kind": "none",
            "hit_token_limit": False,
            "script_error": "",
            "script_timed_out": False,
            "exit_code": 0,
            "reasoning_keyword_impossible": 0,
            "reasoning_keyword_give_up": 0,
            "reasoning_words": 100,
            "script_has_write_answer": True,
            "script_has_python": True,
            "output_chars": 100,
            "tests_in_overview": False,
        }
        cheap = promise_score(
            reward=10, features=features, spent_cost=100, wave2_max_tokens=4000
        )
        expensive = promise_score(
            reward=10, features=features, spent_cost=10000, wave2_max_tokens=4000
        )
        self.assertGreater(cheap, expensive)


class AttemptLoggerTest(unittest.TestCase):
    def test_writes_jsonl_and_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            logger = AttemptLogger(Path(tmp), run_id="run-1")
            logger.log(
                {
                    "task_id": "math_0000",
                    "wave": 1,
                    "answer_kind": "value",
                    "features": {"answer_kind": "value"},
                }
            )
            jsonl = Path(tmp) / "bash_attempts.jsonl"
            self.assertTrue(jsonl.is_file())
            payload = json.loads(jsonl.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(payload["run_id"], "run-1")
            self.assertEqual(payload["task_id"], "math_0000")
            readable = list((Path(tmp) / "readable").glob("*.yaml"))
            self.assertEqual(len(readable), 1)


if __name__ == "__main__":
    unittest.main()
