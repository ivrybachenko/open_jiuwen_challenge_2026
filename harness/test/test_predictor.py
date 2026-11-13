"""Tests for the online success predictor and its fallback."""

from __future__ import annotations

import unittest
from unittest import mock

from harness.solving import scheduler as scheduler_module
from harness.solving.success_predictors import estimate_success
from harness.solving.success_predictors.model import available, predict_success


def _sample_features() -> dict:
    return {
        "task_type": "coding",
        "reward": 5.0,
        "input_tokens": 700,
        "output_tokens": 180,
        "cost": 250,
        "reasoning_chars": 0,
        "reasoning_words": 0,
        "output_chars": 120,
        "output_lines": 3,
        "script_chars": 500,
        "script_lines": 8,
        "script_words": 60,
        "answer_chars": 10,
        "overview_chars": 900,
        "overview_lines": 20,
        "hit_token_limit": False,
        "timed_out": False,
        "tests_in_overview": True,
        "reasoning_keyword_impossible": 0,
        "reasoning_keyword_give_up": 0,
        "script_has_python": True,
        "script_has_tests": True,
        "script_has_file_ops": True,
        "script_has_write_answer": True,
        "script_mentions_impossible": False,
        "answer_present": True,
        "answer_impossible": False,
        "exit_bad": False,
        "answer_kind": "done",
        "n_cat": 1,
        "n_grep": 0,
        "n_find": 0,
        "n_ls": 1,
        "n_head": 0,
        "n_tail": 0,
        "n_awk": 0,
        "n_sed": 0,
        "n_sort": 0,
        "n_wc": 0,
        "n_python": 1,
        "n_test": 1,
        "n_for": 1,
        "n_while": 0,
        "n_if": 0,
        "n_pipe": 1,
        "n_semicolon": 0,
        "n_redirect": 1,
        "n_echo": 1,
        "n_impossible": 0,
    }


class OnlinePredictorTest(unittest.TestCase):
    def test_model_files_load(self) -> None:
        self.assertTrue(available())

    def test_probability_in_range(self) -> None:
        probability = predict_success(_sample_features())
        self.assertIsNotNone(probability)
        assert probability is not None
        self.assertGreaterEqual(probability, 0.0)
        self.assertLessEqual(probability, 1.0)

    def test_promise_uses_model_probability(self) -> None:
        sample = _sample_features()
        with mock.patch.object(
            scheduler_module, "estimate_success", return_value=0.9
        ):
            high = scheduler_module.promise_score(
                reward=5, features=sample, spent_cost=300, wave2_max_tokens=4000
            )
        with mock.patch.object(
            scheduler_module, "estimate_success", return_value=0.1
        ):
            low = scheduler_module.promise_score(
                reward=5, features=sample, spent_cost=300, wave2_max_tokens=4000
            )
        self.assertGreater(high, low)

    def test_fallback_when_model_is_unavailable(self) -> None:
        sample = dict(
            _sample_features(),
            answer_kind="none",
            answer_present=False,
            answer_chars=0,
        )
        with mock.patch(
            "harness.solving.success_predictors.predict_success", return_value=None
        ):
            value = estimate_success(sample)
        self.assertGreater(value, 0.0)


if __name__ == "__main__":
    unittest.main()
