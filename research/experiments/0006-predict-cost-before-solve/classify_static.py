#!/usr/bin/env python3
"""Clean classification and cross-version numbers for experiment 0006.

Features are the honest set: no ``solvable``/``check``/``expected`` and no
``cost_current_wave*`` targets.  RF only, three splits, saved as JSON.

Usage::

    harness/.venv/bin/python \
        research/experiments/0006-predict-cost-before-solve/classify_static.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[2]
sys.path.insert(0, str(EXP))
import train_static as ts  # noqa: E402


def main() -> int:
    args = SimpleNamespace(
        current_runs=EXP / "results" / "current_runs.csv",
        examples_runs=EXP / "results" / "example_runs.csv",
        v0001=ROOT / "data" / "harness_task_score" / "harness_v_0001.tsv",
        overview=EXP / "results" / "overview_features.csv",
    )
    df = ts._load_targets(args, pd.read_csv(EXP / "results" / "static_features.csv"))
    num, cat = ts._features(df)
    report: dict[str, object] = {"features": num + cat}

    # v0001 cost, clean.
    section = {}
    for mode in ("random", "category", "block"):
        base = ts._category_median_baseline(df, "cost_v1_median", mode)
        _, metrics = ts._regression_cv(
            df, "cost_v1_median", num, cat, mode,
            lambda: RandomForestRegressor(
                n_estimators=300, min_samples_leaf=3, random_state=0, n_jobs=1))
        section[f"baseline_{mode}"] = base
        section[f"rf_{mode}"] = metrics
        print("v0001", mode, round(base["mae"], 1), round(metrics["mae"], 1),
              round(metrics["spearman"], 3), flush=True)
    report["cost_v0001"] = section

    # Classification targets.
    targets = {
        "impossible": ("is_impossible_dir", None),
        "correct": ("correct_current_rate", 0.5),
        "answered": ("answered_current_rate", 0.5),
    }
    for key, (target, threshold) in targets.items():
        data = df.dropna(subset=[target]).copy()
        if threshold is None:
            data["y"] = data[target].astype(int)
        else:
            data["y"] = (data[target] >= threshold).astype(int)
        section = {}
        for mode in ("random", "category", "block"):
            _, metrics = ts._classification_cv(
                data, "y", num, cat, mode,
                lambda: RandomForestClassifier(
                    n_estimators=300, min_samples_leaf=3, random_state=0,
                    n_jobs=1))
            section[f"rf_{mode}"] = metrics
            print(key, mode, round(metrics["auc"], 3),
                  round(metrics["pr_auc"], 3), flush=True)
        report[key] = section

    (EXP / "results" / "classification_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote classification_report.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
