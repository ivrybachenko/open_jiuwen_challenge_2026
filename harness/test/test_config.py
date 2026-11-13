"""Unit tests for runtime settings that affect evaluation runs."""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from harness.application.config import Settings


class ModelDefaultTest(unittest.TestCase):
    def test_default_model_is_noreason(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings.from_env(tasks_dir="/tmp/tasks")
        self.assertEqual(settings.model, "qwen3.6-35b-a3b-noreason")

    def test_env_model_overrides_default(self) -> None:
        with patch.dict(os.environ, {"LLM_MODEL": "qwen3.8-27b"}, clear=True):
            settings = Settings.from_env(tasks_dir="/tmp/tasks")
        self.assertEqual(settings.model, "qwen3.8-27b")

    def test_flag_model_overrides_env(self) -> None:
        with patch.dict(os.environ, {"LLM_MODEL": "qwen3.8-27b"}, clear=True):
            settings = Settings.from_env(
                tasks_dir="/tmp/tasks",
                model="qwen3.6-35b-a3b",
            )
        self.assertEqual(settings.model, "qwen3.6-35b-a3b")


class TrajectoriesDirTest(unittest.TestCase):
    def test_disabled_without_flag_or_env(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings.from_env(tasks_dir="/tmp/tasks")
        self.assertIsNone(settings.trajectories_dir)

    def test_env_variable_is_used(self) -> None:
        with patch.dict(
            os.environ, {"TRAJECTORIES_DIR": "/tmp/traces"}, clear=True
        ):
            settings = Settings.from_env(tasks_dir="/tmp/tasks")
        self.assertEqual(settings.trajectories_dir, Path("/tmp/traces"))

    def test_flag_overrides_env(self) -> None:
        with patch.dict(
            os.environ, {"TRAJECTORIES_DIR": "/tmp/from-env"}, clear=True
        ):
            settings = Settings.from_env(
                tasks_dir="/tmp/tasks",
                trajectories_dir="/tmp/from-flag",
            )
        self.assertEqual(settings.trajectories_dir, Path("/tmp/from-flag"))

    def test_run_id_is_optional(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings.from_env(tasks_dir="/tmp/tasks")
        self.assertIsNone(settings.run_id)

    def test_run_id_from_env_and_flag(self) -> None:
        with patch.dict(os.environ, {"HARNESS_RUN_ID": "env-run"}, clear=True):
            from_env = Settings.from_env(tasks_dir="/tmp/tasks")
            from_flag = Settings.from_env(
                tasks_dir="/tmp/tasks",
                run_id="flag-run",
            )
        self.assertEqual(from_env.run_id, "env-run")
        self.assertEqual(from_flag.run_id, "flag-run")


class WaveSettingsTest(unittest.TestCase):
    def test_defaults(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings.from_env(tasks_dir="/tmp/tasks")
        self.assertEqual(settings.wave1_max_tokens, 1000)
        self.assertEqual(settings.wave2_max_tokens, 4000)
        self.assertEqual(settings.wave2_max_tasks, 50)
        self.assertEqual(settings.overview_max_tokens, 1500)
        self.assertTrue(settings.resume)

    def test_max_waves_defaults_to_four(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings.from_env(tasks_dir="/tmp/tasks")
        self.assertEqual(settings.max_waves, 4)

    def test_max_waves_from_env_and_flag(self) -> None:
        with patch.dict(os.environ, {"HARNESS_MAX_WAVES": "3"}, clear=True):
            from_env = Settings.from_env(tasks_dir="/tmp/tasks")
            from_flag = Settings.from_env(tasks_dir="/tmp/tasks", max_waves=2)
        self.assertEqual(from_env.max_waves, 3)
        self.assertEqual(from_flag.max_waves, 2)

    def test_flags_override_defaults(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings.from_env(
                tasks_dir="/tmp/tasks",
                wave1_max_tokens=700,
                wave2_max_tokens=3000,
                wave2_max_tasks=7,
                overview_max_tokens=900,
                script_output_max_chars=1200,
                turn_timeout=30,
                model_timeout=90,
                resume=False,
            )
        self.assertEqual(settings.wave1_max_tokens, 700)
        self.assertEqual(settings.wave2_max_tokens, 3000)
        self.assertEqual(settings.wave2_max_tasks, 7)
        self.assertEqual(settings.overview_max_tokens, 900)
        self.assertEqual(settings.script_output_max_chars, 1200)
        self.assertEqual(settings.turn_timeout, 30)
        self.assertEqual(settings.model_timeout, 90)
        self.assertFalse(settings.resume)

    def test_environment_is_used(self) -> None:
        with patch.dict(
            os.environ,
            {
                "HARNESS_WAVE1_MAX_TOKENS": "500",
                "HARNESS_WAVE2_MAX_TOKENS": "2500",
                "HARNESS_RESUME": "0",
            },
            clear=True,
        ):
            settings = Settings.from_env(tasks_dir="/tmp/tasks")
        self.assertEqual(settings.wave1_max_tokens, 500)
        self.assertEqual(settings.wave2_max_tokens, 2500)
        self.assertFalse(settings.resume)


class BudgetSettingsTest(unittest.TestCase):
    def test_default_budget_is_100k(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings.from_env(tasks_dir="/tmp/tasks")
        self.assertEqual(settings.budget, 100_000)

    def test_budget_env_is_used(self) -> None:
        with patch.dict(os.environ, {"BUDGET": "55000"}, clear=True):
            settings = Settings.from_env(tasks_dir="/tmp/tasks")
        self.assertEqual(settings.budget, 55_000)

    def test_flag_overrides_budget_env(self) -> None:
        with patch.dict(os.environ, {"BUDGET": "55000"}, clear=True):
            settings = Settings.from_env(tasks_dir="/tmp/tasks", budget=8000)
        self.assertEqual(settings.budget, 8_000)

    def test_legacy_env_names_are_ignored(self) -> None:
        with patch.dict(
            os.environ,
            {"TOKEN_BUDGET": "123", "LLM_TOKEN_BUDGET": "456"},
            clear=True,
        ):
            settings = Settings.from_env(tasks_dir="/tmp/tasks")
        self.assertEqual(settings.budget, 100_000)

    def test_invalid_budget_env_falls_back_to_default(self) -> None:
        with patch.dict(os.environ, {"BUDGET": "not-a-number"}, clear=True):
            settings = Settings.from_env(tasks_dir="/tmp/tasks")
        self.assertEqual(settings.budget, 100_000)

    def test_zero_budget_is_kept(self) -> None:
        with patch.dict(os.environ, {"BUDGET": "0"}, clear=True):
            settings = Settings.from_env(tasks_dir="/tmp/tasks")
        self.assertEqual(settings.budget, 0)


class Wave2ModelTest(unittest.TestCase):
    def test_defaults_to_main_model(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings.from_env(
                tasks_dir="/tmp/tasks", model="qwen3.8-27b"
            )
        self.assertEqual(settings.wave2_model, "qwen3.8-27b")

    def test_env_override(self) -> None:
        with patch.dict(
            os.environ, {"LLM_WAVE2_MODEL": "qwen3.6-35b-a3b"}, clear=True
        ):
            settings = Settings.from_env(tasks_dir="/tmp/tasks")
        self.assertEqual(settings.wave2_model, "qwen3.6-35b-a3b")

    def test_flag_overrides_env(self) -> None:
        with patch.dict(
            os.environ, {"LLM_WAVE2_MODEL": "qwen3.6-35b-a3b"}, clear=True
        ):
            settings = Settings.from_env(
                tasks_dir="/tmp/tasks", wave2_model="qwen3.8-27b"
            )
        self.assertEqual(settings.wave2_model, "qwen3.8-27b")


if __name__ == "__main__":
    unittest.main()
