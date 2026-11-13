#!/usr/bin/env python3
"""Fast report for the static predictor (RF only).

The full ``train_static.py`` sweeps three model families over four splits and
takes tens of minutes.  This script computes the numbers needed for the
experiment record with one model family and saves the same predictor bundle.

Usage::

    harness/.venv/bin/python \
        research/experiments/0006-predict-cost-before-solve/report_static_light.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    average_precision_score, mean_absolute_error, r2_score, roc_auc_score,
)
from sklearn.pipeline import Pipeline

EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[2]
sys.path.insert(0, str(EXP))
import train_static as ts  # noqa: E402


def _rf_reg():
    return RandomForestRegressor(
        n_estimators=300, min_samples_leaf=3, random_state=0, n_jobs=1)


def _rf_clf():
    return RandomForestClassifier(
        n_estimators=300, min_samples_leaf=3, random_state=0, n_jobs=1)


def _baseline(df: pd.DataFrame, target: str, mode: str) -> dict[str, float]:
    return ts._category_median_baseline(df, target, mode)


def main() -> int:
    args = SimpleNamespace(
        current_runs=EXP / "results" / "current_runs.csv",
        examples_runs=EXP / "results" / "example_runs.csv",
        v0001=ROOT / "data" / "harness_task_score" / "harness_v_0001.tsv",
        overview=EXP / "results" / "overview_features.csv",
    )
    tasks = pd.read_csv(EXP / "results" / "static_features.csv")
    df = ts._load_targets(args, tasks)
    num, cat = ts._features(df)
    report: dict[str, object] = {"tasks": len(df), "features": num + cat}

    # Current cost.
    target = "cost_current_mean"
    print("== current cost ==", flush=True)
    cost_report: dict[str, object] = {}
    for mode in ("random", "category", "block"):
        base = _baseline(df, target, mode)
        pred, metrics = ts._regression_cv(df, target, num, cat, mode, _rf_reg)
        cost_report[f"baseline_{mode}"] = base
        cost_report[f"rf_{mode}"] = metrics
        print(mode, "baseline", round(base["mae"], 1), round(base["spearman"], 3),
              "rf", round(metrics["mae"], 1), round(metrics["spearman"], 3),
              flush=True)
        if mode == "random":
            data = df.dropna(subset=[target])
            pd.DataFrame({
                "rel": data["rel"].values,
                "task_type": data["task_type"].values,
                "impossible": data["is_impossible_dir"].values,
                "actual": data[target].values,
                "predicted": pred,
            }).to_csv(EXP / "results" / "static_predictions.csv", index=False)
            y = data[target].astype(float).values
            cost_report["bootstrap"] = ts._bootstrap_regression(y, pred)
    report["cost_current"] = cost_report

    # v0001 and exp0002 (random split only).
    for target, label in (("cost_v1_median", "v0001"),
                          ("cost_exp0002", "exp0002")):
        if target not in df:
            continue
        base = _baseline(df, target, "random")
        _, metrics = ts._regression_cv(df, target, num, cat, "random", _rf_reg)
        report[f"cost_{label}"] = {"baseline": base, "rf": metrics}
        print(label, "baseline", round(base["mae"], 1), "rf",
              round(metrics["mae"], 1), round(metrics["spearman"], 3), flush=True)

    # Solvability (honest and leak) and solved-correctly.
    for target, key in (("is_impossible_dir", "impossible"),
                        ("correct_current_rate", "correct")):
        print(f"== {key} ==", flush=True)
        data = df.dropna(subset=[target]).copy()
        if key == "correct":
            data["y"] = (data[target] >= 0.5).astype(int)
        else:
            data["y"] = data[target].astype(int)
        target_col = "y"
        section: dict[str, object] = {}
        for mode in ("random", "category", "block"):
            _, metrics = ts._classification_cv(
                data, target_col, num, cat, mode, _rf_clf)
            section[f"rf_{mode}"] = metrics
            print(mode, round(metrics["auc"], 3), round(metrics["pr_auc"], 3),
                  flush=True)
        report[key] = section

    # Leak model.
    leak_path = EXP / "results" / "static_features_leak.csv"
    if leak_path.is_file():
        leak = pd.read_csv(leak_path)
        leak = ts._load_targets(args, leak)
        leak_num, leak_cat = ts._features(leak, leak=True)
        section = {}
        for mode in ("random", "category", "block"):
            _, metrics = ts._classification_cv(
                leak, "is_impossible_dir", leak_num, leak_cat, mode, _rf_clf)
            section[f"leak_rf_{mode}"] = metrics
            print("leak", mode, round(metrics["auc"], 3), flush=True)
        report["impossible_leak"] = section

    # Answered in wave 1.
    if "answered_current_rate" in df:
        print("== answered ==", flush=True)
        data = df.dropna(subset=["answered_current_rate"]).copy()
        data["y"] = (data["answered_current_rate"] >= 0.5).astype(int)
        section = {}
        for mode in ("random", "category", "block"):
            _, metrics = ts._classification_cv(
                data, "y", num, cat, mode, _rf_clf)
            section[f"rf_{mode}"] = metrics
            print(mode, round(metrics["auc"], 3), round(metrics["pr_auc"], 3),
                  flush=True)
        report["answered_wave1"] = section

    # Two-stage cost.
    print("== two-stage ==", flush=True)
    data = df.dropna(subset=["cost_current_mean", "answered_current_rate",
                             "cost_current_wave1"]).copy()
    data["answered_any"] = (data["answered_current_rate"] >= 0.5).astype(int)
    p_ans = ts._oof_classifier(data, "answered_any", num, cat)
    am = data["answered_any"] == 1
    cost_answered = ts._oof_regression(
        data, "cost_current_wave1", am, num, cat)
    cost_unanswered = ts._oof_regression(
        data, "cost_current_mean", ~am, num, cat)
    combined = (p_ans * cost_answered.fillna(0.0)
                + (1.0 - p_ans) * cost_unanswered.fillna(0.0))
    valid = combined.notna() & data["cost_current_mean"].notna()
    y = data.loc[valid, "cost_current_mean"].astype(float).values
    pred = combined[valid].values
    if len(y) >= 5:
        report["two_stage"] = {
            "n": int(len(y)),
            "mae": float(mean_absolute_error(y, pred)),
            "r2": float(r2_score(y, pred)),
            "spearman": ts._spearman(y, pred),
            "bootstrap_mae_ci": ts._bootstrap_regression(y, pred)["mae_ci"],
        }
        print(report["two_stage"], flush=True)

    # Built-in importance (fast).
    data = df.dropna(subset=[target]).copy()
    pipe = Pipeline([
        ("pre", ts._pre(num, cat)),
        ("model", _rf_reg()),
    ])
    y_log = np.log1p(data[target].astype(float))
    pipe.fit(data[num + cat], y_log)
    importances = pipe.named_steps["model"].feature_importances_
    names = num + list(
        pipe.named_steps["pre"].named_transformers_["cat"]
        .get_feature_names_out(cat))
    order = np.argsort(importances)[::-1][:20]
    report["importance"] = [
        {"feature": names[i], "importance": float(importances[i])}
        for i in order
    ]
    print("top", [item["feature"] for item in report["importance"][:10]], flush=True)

    ts._write_predictor(df, num, cat, EXP / "results")
    (EXP / "results" / "static_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote static_report.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
