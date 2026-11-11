"""Unit tests for runtime settings that affect evaluation runs."""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from harness.application.config import Settings


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


if __name__ == "__main__":
    unittest.main()
