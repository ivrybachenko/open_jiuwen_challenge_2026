#!/usr/bin/env python3
"""Aggregate pre-solve overview signals from turn-level logs.

``turn_groups.csv`` is produced by experiment 0007 and contains the wave-1
overview the harness built *before* the first model call.  This script reduces
it to one row per task so the static predictor can use the overview length,
file count and test-failure signals.

Usage::

    harness/.venv/bin/python \
        research/experiments/0006-predict-cost-before-solve/overview_features.py \
        --groups research/experiments/0007-predict-remaining-cost-during-solve/results/turn_groups.csv \
        --out research/experiments/0006-predict-cost-before-solve/results/overview_features.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

COLUMNS = [
    "overview_chars", "overview_lines", "overview_fails", "overview_passes",
    "overview_notimplemented", "overview_asserts", "overview_syntax",
    "overview_typeerror", "overview_filenames", "overview_dollar_lines",
    "tests_in_overview",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--groups", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    df = pd.read_csv(args.groups)
    present = [c for c in COLUMNS if c in df.columns]
    agg = df.groupby("rel")[present].median()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    agg.to_csv(args.out)
    print(f"wrote {len(agg)} tasks x {len(present)} overview features to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
