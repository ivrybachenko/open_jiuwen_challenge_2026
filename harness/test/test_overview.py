"""Unit tests for the bounded workspace overview."""

from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from harness.infrastructure.overview import OverviewLimits, build_overview


class OverviewTest(unittest.TestCase):
    def test_identical_dataset_headers_are_printed_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(3):
                (root / f"part{index}.csv").write_text(
                    "id,name,value\n1,Alice,10\n2,Bob,20\n",
                    encoding="utf-8",
                )
            text = build_overview(root, "sum values")
            self.assertIn("same header: id,name,value", text)
            self.assertIn("example row: 1,Alice,10", text)
            self.assertEqual(text.count("same header:"), 1)

    def test_long_header_and_row_are_truncated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "wide.csv").write_text(
                "x" * 20_000 + "\n" + "y" * 20_000 + "\n",
                encoding="utf-8",
            )
            text = build_overview(root, "read it")
            self.assertIn("[truncated]", text)
            self.assertLess(len(text), 20_000)

    def test_many_files_are_collapsed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            data.mkdir()
            for index in range(300):
                (data / f"part{index:04d}.csv").write_text(
                    "a,b\n1,2\n", encoding="utf-8"
                )
            text = build_overview(root, "use data")
            self.assertIn("data/*.csv", text)
            self.assertLess(text.count("data/part"), 10)

    def test_overview_respects_token_cap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(2000):
                (root / f"file{index:04d}.txt").write_text(
                    "some text\n", encoding="utf-8"
                )
            limits = OverviewLimits(max_tokens=300)
            text = build_overview(root, "task " * 2000, limits)
            self.assertLessEqual(len(text), limits.max_chars)
            self.assertIn("$ cat task.txt", text)

    def test_large_file_is_not_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "large.bin").write_bytes(b"x" * (6 * 1024 * 1024))
            text = build_overview(root, "inspect")
            self.assertIn("large.bin", text)
            self.assertIn("(6.0 MB)", text)

    def test_binary_dataset_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "binary.csv").write_bytes(b"a,b\x00c\n1,2,3\n")
            text = build_overview(root, "inspect")
            self.assertNotIn("a,b", text)

    def test_passing_tests_are_shown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test_ok.py").write_text(
                "import unittest\n"
                "class T(unittest.TestCase):\n"
                "    def test_ok(self):\n"
                "        self.assertEqual(1, 1)\n"
                "if __name__ == '__main__':\n"
                "    unittest.main()\n",
                encoding="utf-8",
            )
            text = build_overview(root, "run tests")
            self.assertIn("test_ok.py: PASS", text)

    def test_failing_tests_show_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test_bad.py").write_text(
                "import unittest\n"
                "class T(unittest.TestCase):\n"
                "    def test_bad(self):\n"
                "        self.assertEqual(1, 2)\n"
                "if __name__ == '__main__':\n"
                "    unittest.main()\n",
                encoding="utf-8",
            )
            text = build_overview(root, "run tests")
            self.assertIn("test_bad.py: FAIL", text)
            self.assertIn("AssertionError", text)

    def test_hanging_test_is_stopped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test_slow.py").write_text(
                "import time\nprint('start', flush=True)\ntime.sleep(5)\n",
                encoding="utf-8",
            )
            limits = OverviewLimits(test_timeout=0.3, test_total_timeout=1.0)
            started = time.monotonic()
            text = build_overview(root, "run tests", limits)
            self.assertLess(time.monotonic() - started, 4.0)
            self.assertIn("TIMEOUT", text)


if __name__ == "__main__":
    unittest.main()
