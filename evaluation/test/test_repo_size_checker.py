"""Tests for the repository size checker (stdlib unittest only)."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from evaluation.repo_size_checker.checker import check_repo_size, scan_tree

GIT = shutil.which("git")


def write(path: Path, size: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)


class ScanTreeTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_counts_files_per_root_entry(self) -> None:
        write(self.root / "a.txt", 10)
        write(self.root / "src" / "b.py", 20)
        write(self.root / "src" / "deep" / "c.py", 30)
        write(self.root / ".git" / "config", 5)

        total, usage, largest = scan_tree(self.root, largest_n=3)

        self.assertEqual(65, total)
        self.assertEqual((10, 1), usage["a.txt"])
        self.assertEqual((50, 2), usage["src"])
        self.assertEqual((5, 1), usage[".git"])
        self.assertEqual(
            ["src/deep/c.py", "src/b.py", "a.txt"],
            [entry.path for entry in largest],
        )

    def test_does_not_follow_symlinks(self) -> None:
        write(self.root / "target" / "big.bin", 1000)
        link = self.root / "link"
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks are not supported")
        try:
            link.symlink_to(self.root / "target", target_is_directory=True)
        except OSError:
            self.skipTest("cannot create symlinks")

        total, usage, _ = scan_tree(self.root)

        # The link is counted as a small entry of its own, the target once.
        self.assertLess(total, 1000 + 200)
        self.assertIn("target", usage)
        self.assertIn("link", usage)

    def test_counts_dangling_symlink_itself(self) -> None:
        write(self.root / "ok.txt", 3)
        missing = self.root / "missing.txt"
        try:
            missing.symlink_to(self.root / "does-not-exist")
        except OSError:
            self.skipTest("cannot create symlinks")

        total, usage, _ = scan_tree(self.root)

        self.assertEqual((3, 1), usage["ok.txt"])
        self.assertGreater(usage["missing.txt"][0], 0)
        self.assertEqual(3 + usage["missing.txt"][0], total)


class RepoSizeTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def git(self, *args: str) -> None:
        subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def test_tracked_metric_ignores_local_files(self) -> None:
        if GIT is None:
            self.skipTest("git is not installed")
        self.git("init")
        write(self.repo / "tracked.txt", 40)
        write(self.repo / ".gitignore", 0)
        self.git("add", "tracked.txt", ".gitignore")
        write(self.repo / ".venv" / "lib.bin", 10_000)

        report = check_repo_size(repo=self.repo, max_bytes=1000, metric="tracked")

        self.assertEqual(40, report.tracked_bytes)
        self.assertEqual(2, report.tracked_files)
        self.assertGreater(report.without_git_bytes, 10_000)
        self.assertEqual(40, report.measured_bytes)
        self.assertTrue(report.ok)
        self.assertEqual(10_000, report.untracked_bytes)
        self.assertEqual(
            {"tracked.txt": 40, ".gitignore": 0},
            {
                entry.name: entry.tracked_bytes
                for entry in report.top_level
                if entry.name in {"tracked.txt", ".gitignore"}
            },
        )

    def test_without_git_metric_includes_local_files(self) -> None:
        write(self.repo / "file.bin", 100)
        report = check_repo_size(repo=self.repo, max_bytes=1000, metric="without-git")

        self.assertGreaterEqual(report.measured_bytes, 100)
        self.assertTrue(report.ok)
        self.assertEqual(report.total_bytes - report.git_bytes, report.measured_bytes)

    def test_limit_is_enforced(self) -> None:
        write(self.repo / "file.bin", 100)
        report = check_repo_size(repo=self.repo, max_bytes=10, metric="without-git")

        self.assertFalse(report.ok)
        self.assertEqual("without-git", report.metric)
        self.assertIn("without .git", report.measured_source)

    def test_rejects_unknown_metric(self) -> None:
        with self.assertRaises(ValueError):
            check_repo_size(repo=self.repo, metric="nonsense")

    def test_rejects_missing_directory(self) -> None:
        with self.assertRaises(NotADirectoryError):
            check_repo_size(repo=self.repo / "missing")

    def test_report_serializes(self) -> None:
        write(self.repo / "file.bin", 10)
        payload = check_repo_size(repo=self.repo).to_dict()

        self.assertEqual(str(self.repo.resolve()), payload["repo"])
        self.assertIn("without_git_bytes", payload["sizes"])
        self.assertEqual("tracked", payload["metric"])
        self.assertIsInstance(payload["top_level"], list)


if __name__ == "__main__":
    unittest.main()
