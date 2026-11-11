"""Integrity checks for the score datasets stored in ``data/``."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class ScoreDatasetIntegrityTest(unittest.TestCase):
    def test_run_id_is_unique_in_every_dataset(self) -> None:
        paths = sorted((REPO_ROOT / "data").glob("*/harness_v_*.tsv"))
        self.assertTrue(paths, "no score datasets found under data/")

        for path in paths:
            with self.subTest(path=path):
                lines = path.read_text(encoding="utf-8").splitlines()
                header = lines[0].split("\t")
                run_index = header.index("run_id")
                run_ids = [line.split("\t")[run_index] for line in lines[1:]]
                self.assertTrue(all(run_ids), f"empty run_id in {path}")
                self.assertEqual(
                    len(set(run_ids)),
                    len(run_ids),
                    f"duplicate run_id in {path}",
                )


if __name__ == "__main__":
    unittest.main()
