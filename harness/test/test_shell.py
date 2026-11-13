"""Unit tests for bounded shell execution."""

from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from harness.infrastructure.shell import run_process


class RunProcessTest(unittest.TestCase):
    def test_captures_stdout_stderr_and_exit_code(self) -> None:
        result = run_process(
            ["bash", "-c", "echo out; echo err >&2; exit 3"],
            cwd=".",
            timeout=5,
        )
        self.assertEqual(result.exit_code, 3)
        self.assertIn("out", result.output)
        self.assertIn("err", result.output)
        self.assertFalse(result.timed_out)

    def test_timeout_kills_the_group(self) -> None:
        started = time.monotonic()
        result = run_process(
            ["bash", "-c", "sleep 5"],
            cwd=".",
            timeout=0.3,
        )
        self.assertTrue(result.timed_out)
        self.assertEqual(result.exit_code, 124)
        self.assertLess(time.monotonic() - started, 4.0)

    def test_output_is_bounded(self) -> None:
        result = run_process(
            ["bash", "-c", "python3 -c \"print('x' * 200000)\""],
            cwd=".",
            timeout=10,
            max_output_chars=500,
        )
        self.assertLessEqual(len(result.output), 700)
        self.assertIn("truncated", result.output)

    def test_missing_command_does_not_raise(self) -> None:
        result = run_process(
            ["definitely-not-a-command-xyz"],
            cwd=".",
            timeout=2,
        )
        self.assertTrue(result.error)

    def test_tail_command_written_by_agent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "step.sh"
            script.write_text("echo 42 > answer.txt\n", encoding="utf-8")
            result = run_process(["bash", str(script)], cwd=root, timeout=5)
            self.assertTrue(result.ok)
            self.assertEqual((root / "answer.txt").read_text().strip(), "42")


if __name__ == "__main__":
    unittest.main()
