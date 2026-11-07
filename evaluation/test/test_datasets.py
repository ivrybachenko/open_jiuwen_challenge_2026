"""Tests for the harness score dataset writers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from evaluation.common.datasets import (
    clear_task_scores,
    clear_task_set_scores,
    current_harness_version,
    ensure_harness_info,
    has_harness_info,
    record_task_score,
    record_task_set_score,
    resolve_harness_version,
)


class DatasetWriterTest(unittest.TestCase):
    def _repo(self, base: Path) -> Path:
        (base / "harness").mkdir()
        (base / "harness" / "pyproject.toml").write_text(
            '[project]\nname = "x"\nversion = "0001"\n',
            encoding="utf-8",
        )
        return base

    def test_version_from_pyproject(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            self.assertEqual(current_harness_version(repo), "0001")

    def test_version_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            self.assertEqual(resolve_harness_version(repo, "0001"), "0001")
            with self.assertRaises(ValueError):
                resolve_harness_version(repo, "0002")

    def test_task_score_upsert_and_tsv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            path = record_task_score(
                repo,
                task_id="coding/easy/0001",
                harness_version="0001",
                run_id="r1",
                is_solved_correctly=False,
                cost_tokens=100,
                cost_seconds=12.3456,
            )
            record_task_score(
                repo,
                task_id="coding/easy/0001",
                harness_version="0001",
                run_id="r1",
                is_solved_correctly=True,
                cost_tokens=200,
                cost_seconds=20.0,
            )
            record_task_score(
                repo,
                task_id="math/easy/0001",
                harness_version="0001",
                run_id="r1",
                is_solved_correctly=True,
                cost_tokens=50,
                cost_seconds=5.0,
            )
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(
                lines[0],
                "harness_version\trun_id\ttask_id\tis_solved_correctly\t"
                "cost_tokens\tcost_seconds",
            )
            self.assertEqual(
                lines[1],
                "0001\tr1\tcoding/easy/0001\ttrue\t200\t20.000",
            )
            self.assertEqual(
                lines[2],
                "0001\tr1\tmath/easy/0001\ttrue\t50\t5.000",
            )
            self.assertEqual(len(lines), 3)

    def test_task_score_separate_run_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            path = record_task_score(
                repo,
                task_id="coding/easy/0001",
                harness_version="0001",
                run_id="r1",
                is_solved_correctly=True,
                cost_tokens=100,
                cost_seconds=1.0,
            )
            record_task_score(
                repo,
                task_id="coding/easy/0001",
                harness_version="0001",
                run_id="r2",
                is_solved_correctly=False,
                cost_tokens=200,
                cost_seconds=2.0,
            )
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 3)
            self.assertIn("0001\tr1\tcoding/easy/0001\ttrue\t100\t1.000", lines)
            self.assertIn("0001\tr2\tcoding/easy/0001\tfalse\t200\t2.000", lines)

    def test_old_task_score_header_is_migrated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            path = (
                repo
                / "data"
                / "harness_task_score"
                / "harness_v_0001.tsv"
            )
            path.parent.mkdir(parents=True)
            path.write_text(
                "task_id\tharness_version\tcost_tokens\tcost_seconds\n"
                "coding/easy/0001\t0001\t100\t1.000\n",
                encoding="utf-8",
            )
            record_task_score(
                repo,
                task_id="math/easy/0001",
                harness_version="0001",
                run_id="r1",
                is_solved_correctly=True,
                cost_tokens=50,
                cost_seconds=5.0,
            )
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(
                lines[0],
                "harness_version\trun_id\ttask_id\tis_solved_correctly\t"
                "cost_tokens\tcost_seconds",
            )
            self.assertEqual(
                lines[1],
                "0001\t\tcoding/easy/0001\t\t100\t1.000",
            )
            self.assertEqual(
                lines[2],
                "0001\tr1\tmath/easy/0001\ttrue\t50\t5.000",
            )

    def test_task_set_score_upsert(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            path = record_task_set_score(
                repo,
                task_set_id="minimal",
                harness_version="0001",
                run_id="r1",
                score=5.0,
                cost_tokens=300,
                cost_seconds=60.5,
            )
            record_task_set_score(
                repo,
                task_set_id="minimal",
                harness_version="0001",
                run_id="r1",
                score=3.0,
                cost_tokens=200,
                cost_seconds=30.0,
            )
            record_task_set_score(
                repo,
                task_set_id="minimal",
                harness_version="0001",
                run_id="r2",
                score=4.0,
                cost_tokens=250,
                cost_seconds=40.0,
            )
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(
                lines[0],
                "harness_version\trun_id\ttask_set_id\tscore\t"
                "cost_tokens\tcost_seconds",
            )
            self.assertEqual(lines[1], "0001\tr1\tminimal\t3\t200\t30.000")
            self.assertEqual(lines[2], "0001\tr2\tminimal\t4\t250\t40.000")

    def test_clear_datasets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            task_path = record_task_score(
                repo,
                task_id="coding/easy/0001",
                harness_version="0001",
                run_id="r1",
                is_solved_correctly=True,
                cost_tokens=100,
                cost_seconds=1.0,
            )
            set_path = record_task_set_score(
                repo,
                task_set_id="minimal",
                harness_version="0001",
                run_id="r1",
                score=5.0,
                cost_tokens=300,
                cost_seconds=60.0,
            )
            clear_task_scores(repo, "0001")
            clear_task_set_scores(repo, "0001")
            self.assertEqual(
                task_path.read_text(encoding="utf-8").count("\n"),
                1,
            )
            self.assertEqual(
                set_path.read_text(encoding="utf-8").count("\n"),
                1,
            )

    def test_harness_info_presence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            self.assertFalse(has_harness_info(repo, "0001"))
            ensure_harness_info(
                repo,
                harness_version="0001",
                description="first",
            )
            self.assertTrue(has_harness_info(repo, "0001"))
            self.assertFalse(has_harness_info(repo, "0002"))

    def test_harness_info_normalizes_and_keeps_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            info = repo / "data" / "harness_info" / "harness_info.tsv"
            info.parent.mkdir(parents=True)
            info.write_text(
                "harness_version parent_harness_version  description\n"
                "0001    0000   Навайбкодил минимальный харнесс.\n",
                encoding="utf-8",
            )
            ensure_harness_info(repo, harness_version="0001")
            lines = info.read_text(encoding="utf-8").splitlines()
            self.assertEqual(
                lines[0],
                "harness_version\tparent_harness_version\tdescription",
            )
            self.assertEqual(
                lines[1],
                "0001\t0000\tНавайбкодил минимальный харнесс.",
            )

    def test_harness_info_adds_new_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            ensure_harness_info(repo, harness_version="0001")
            ensure_harness_info(
                repo,
                harness_version="0002",
                description="next version",
            )
            lines = (
                repo / "data" / "harness_info" / "harness_info.tsv"
            ).read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines[1], "0001\t0000\tauto-recorded by evaluation")
            self.assertEqual(lines[2], "0002\t0001\tnext version")


if __name__ == "__main__":
    unittest.main()
