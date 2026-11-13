"""Tests for the online success predictor and its fallback."""

from __future__ import annotations

import json
import os
import unittest
from unittest import mock

from harness.solving import scheduler as scheduler_module
from harness.solving.success_predictors import estimate_success
from harness.solving.success_predictors.model import (
    WAVE_META_PATH,
    _load,
    _numeric_value,
    available,
    available_wave,
    predict_success,
)


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
                reward=5, features=sample, spent_cost=300, turns=1
            )
        with mock.patch.object(
            scheduler_module, "estimate_success", return_value=0.1
        ):
            low = scheduler_module.promise_score(
                reward=5, features=sample, spent_cost=300, turns=1
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

    def test_numeric_feature_adapter(self) -> None:
        features = {
            "script_timed_out": True,
            "script_error": "boom",
            "cost": 12,
        }
        self.assertEqual(_numeric_value(features, "timed_out"), 1.0)
        self.assertEqual(_numeric_value(features, "script_error"), 4.0)
        self.assertEqual(_numeric_value(features, "cost"), 12.0)
        self.assertEqual(_numeric_value({}, "cost"), 0.0)

    def test_wave_models_are_loaded(self) -> None:
        if not WAVE_META_PATH.is_file():
            self.skipTest("wave model artefacts are not present")
        self.assertTrue(available_wave(2))
        with mock.patch.dict(os.environ, {"HARNESS_WAVE_MODELS": "1"}):
            for wave in (2, 3, 4, 5):
                sample = dict(
                    _sample_features(),
                    wave=wave,
                    answer_kind="none",
                    answer_present=False,
                    answer_chars=0,
                )
                probability = predict_success(sample)
                self.assertIsNotNone(probability)
                assert probability is not None
                self.assertGreaterEqual(probability, 0.0)
                self.assertLessEqual(probability, 1.0)

    def test_wave_selection_and_late_fallback(self) -> None:
        if not WAVE_META_PATH.is_file():
            self.skipTest("wave model artefacts are not present")
        base = dict(
            _sample_features(),
            answer_kind="none",
            answer_present=False,
            answer_chars=0,
        )
        with mock.patch.dict(os.environ, {"HARNESS_WAVE_MODELS": "1"}):
            probabilities = {
                wave: predict_success(dict(base, wave=wave))
                for wave in (1, 2, 3, 4, 5)
            }
        self.assertNotEqual(probabilities[1], probabilities[2])
        self.assertNotEqual(probabilities[2], probabilities[3])
        self.assertNotEqual(probabilities[3], probabilities[4])
        # Waves 5+ deliberately reuse the wave-4 model.
        self.assertEqual(probabilities[4], probabilities[5])

    def test_wave_models_are_disabled_by_default(self) -> None:
        base = dict(
            _sample_features(),
            answer_kind="none",
            answer_present=False,
            answer_chars=0,
        )
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("HARNESS_WAVE_MODELS", None)
            wave1 = predict_success(dict(base, wave=1))
            wave2 = predict_success(dict(base, wave=2))
        self.assertEqual(wave1, wave2)

    def test_wave_models_can_be_enabled(self) -> None:
        if not WAVE_META_PATH.is_file():
            self.skipTest("wave model artefacts are not present")
        base = dict(
            _sample_features(),
            answer_kind="none",
            answer_present=False,
            answer_chars=0,
        )
        with mock.patch.dict(os.environ, {"HARNESS_WAVE_MODELS": "1"}):
            wave1 = predict_success(dict(base, wave=1))
            wave2 = predict_success(dict(base, wave=2))
        self.assertNotEqual(wave1, wave2)

    def test_missing_wave_models_fall_back_to_global(self) -> None:
        global_loaded = _load()
        self.assertIsNotNone(global_loaded)
        with mock.patch.dict(os.environ, {"HARNESS_WAVE_MODELS": "1"}), mock.patch(
            "harness.solving.success_predictors.model._load_wave_models",
            return_value=None,
        ):
            base = dict(
                _sample_features(),
                answer_kind="none",
                answer_present=False,
                answer_chars=0,
            )
            wave1 = predict_success(dict(base, wave=1))
            wave2 = predict_success(dict(base, wave=2))
        self.assertEqual(wave1, wave2)

    def test_broken_wave_model_falls_back_to_global(self) -> None:
        global_loaded = _load()
        self.assertIsNotNone(global_loaded)
        assert global_loaded is not None
        _, meta = global_loaded
        broken = mock.Mock()
        broken.predict_proba.side_effect = RuntimeError("broken model")
        with mock.patch.dict(
            os.environ, {"HARNESS_WAVE_MODELS": "1"}
        ), mock.patch(
            "harness.solving.success_predictors.model._load_wave_models",
            return_value=({"2": broken}, meta),
        ):
            sample = dict(
                _sample_features(),
                wave=2,
                answer_kind="none",
                answer_present=False,
                answer_chars=0,
            )
            probability = predict_success(sample)
        self.assertIsNotNone(probability)
        assert probability is not None
        self.assertGreaterEqual(probability, 0.0)
        self.assertLessEqual(probability, 1.0)

    def test_wave_metadata_lists_features(self) -> None:
        if not WAVE_META_PATH.is_file():
            self.skipTest("wave model artefacts are not present")
        meta = json.loads(WAVE_META_PATH.read_text(encoding="utf-8"))
        self.assertIn("2", meta["models"])
        self.assertIn("3", meta["models"])
        self.assertIn("4", meta["models"])
        self.assertIn("numeric_features", meta)
        self.assertIn("categorical_features", meta)


if __name__ == "__main__":
    unittest.main()
