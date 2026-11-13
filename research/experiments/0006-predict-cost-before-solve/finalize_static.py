#!/usr/bin/env python3
"""Finalize the static predictor: metrics on the current target + model bundle.

This intentionally avoids the long model sweep in ``train_static.py`` and the
extra sections of ``report_static_light.py``.  It trains the deployable models
on all 240 tasks and writes the numbers used in the experiment record.

Usage::

    harness/.venv/bin/python \
        research/experiments/0006-predict-cost-before-solve/finalize_static.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline

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
    tasks = pd.read_csv(EXP / "results" / "static_features.csv")
    df = ts._load_targets(args, tasks)
    num, cat = ts._features(df)
    print("features", len(num), "tasks", len(df), flush=True)

    target = "cost_current_mean"
    report: dict[str, object] = {"tasks": len(df), "features": num + cat}

    # Metrics: random, category and block splits.
    metrics: dict[str, object] = {}
    for mode in ("random", "category", "block"):
        base = ts._category_median_baseline(df, target, mode)
        pred, model_metrics = ts._regression_cv(
            df, target, num, cat, mode,
            lambda: RandomForestRegressor(
                n_estimators=300, min_samples_leaf=3, random_state=0, n_jobs=1),
        )
        metrics[f"baseline_{mode}"] = base
        metrics[f"rf_{mode}"] = model_metrics
        print(mode, "baseline", round(base["mae"], 1),
              "rf", round(model_metrics["mae"], 1),
              round(model_metrics["spearman"], 3), flush=True)
        if mode == "random":
            data = df.dropna(subset=[target])
            pd.DataFrame({
                "rel": data["rel"].values,
                "task_type": data["task_type"].values,
                "impossible": data["is_impossible_dir"].values,
                "actual": data[target].values,
                "predicted": pred,
            }).to_csv(EXP / "results" / "static_predictions.csv", index=False)
            metrics["bootstrap_random"] = ts._bootstrap_regression(
                data[target].astype(float).values, pred)
    report["cost_current"] = metrics

    # Deployable bundle.
    cost_data = df.dropna(subset=[target]).copy()
    cost_y = np.log1p(cost_data[target].astype(float))
    cost_pipe = Pipeline([
        ("pre", ts._pre(num, cat)),
        ("model", RandomForestRegressor(
            n_estimators=400, min_samples_leaf=3, random_state=0, n_jobs=1)),
    ])
    cost_pipe.fit(cost_data[num + cat], cost_y)
    import joblib
    joblib.dump(cost_pipe, EXP / "results" / "cost_model.joblib")
    print("cost model fitted", flush=True)

    # Dependency-free linear export (clean features only).
    from sklearn.linear_model import Ridge
    linear = Pipeline([("pre", ts._pre(num, cat)), ("model", Ridge(alpha=10.0))])
    linear.fit(cost_data[num + cat], cost_y)
    pre = linear.named_steps["pre"]
    num_pipe = pre.named_transformers_["num"]
    imputer = num_pipe.named_steps["impute"]
    scaler = num_pipe.named_steps["scale"]
    cat_encoder = pre.named_transformers_["cat"]
    linear_payload = {
        "target": "log1p(mean total cost, current harness v0003)",
        "numeric_features": num,
        "categorical_features": cat,
        "impute_statistics": [float(v) for v in imputer.statistics_],
        "scale_mean": [float(v) for v in scaler.mean_],
        "scale_std": [float(v) for v in scaler.scale_],
        "categories": {
            column: [str(v) for v in values]
            for column, values in zip(cat, cat_encoder.categories_)
        },
        "coefficients": [float(v) for v in
                         linear.named_steps["model"].coef_.ravel()],
        "intercept": float(linear.named_steps["model"].intercept_),
    }
    (EXP / "results" / "linear_cost_model.json").write_text(
        json.dumps(linear_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print("linear export written", flush=True)

    imp = cost_pipe.named_steps["model"].feature_importances_
    names = num + list(
        cost_pipe.named_steps["pre"].named_transformers_["cat"]
        .get_feature_names_out(cat))
    order = np.argsort(imp)[::-1][:20]
    report["importance"] = [
        {"feature": names[i], "importance": float(imp[i])} for i in order
    ]
    print("top", [item["feature"] for item in report["importance"][:10]], flush=True)

    # Two-stage model: P(answer in wave 1), wave-1 cost when answered,
    # total cost when not answered.
    data = df.dropna(subset=[target, "answered_current_rate",
                             "cost_current_wave1"]).copy()
    data["answered_any"] = (data["answered_current_rate"] >= 0.5).astype(int)
    answered_mask = data["answered_any"] == 1
    answered_pipe = Pipeline([
        ("pre", ts._pre(num, cat)),
        ("model", RandomForestClassifier(
            n_estimators=400, min_samples_leaf=3, random_state=0, n_jobs=1)),
    ])
    answered_pipe.fit(data[num + cat], data["answered_any"])
    joblib.dump(answered_pipe, EXP / "results" / "answered_model.joblib")

    cost_answered_pipe = Pipeline([
        ("pre", ts._pre(num, cat)),
        ("model", RandomForestRegressor(
            n_estimators=400, min_samples_leaf=3, random_state=0, n_jobs=1)),
    ])
    cost_answered_pipe.fit(
        data.loc[answered_mask, num + cat],
        np.log1p(data.loc[answered_mask, "cost_current_wave1"].astype(float)))
    joblib.dump(cost_answered_pipe, EXP / "results" / "cost_answered_model.joblib")

    cost_unanswered_pipe = Pipeline([
        ("pre", ts._pre(num, cat)),
        ("model", RandomForestRegressor(
            n_estimators=400, min_samples_leaf=3, random_state=0, n_jobs=1)),
    ])
    cost_unanswered_pipe.fit(
        data.loc[~answered_mask, num + cat],
        np.log1p(data.loc[~answered_mask, target].astype(float)))
    joblib.dump(cost_unanswered_pipe, EXP / "results" / "cost_unanswered_model.joblib")
    print("two-stage models fitted", flush=True)

    # Out-of-fold estimate of the two-stage expected cost.
    p_ans = ts._oof_classifier(data, "answered_any", num, cat)
    cost_ans = ts._oof_regression(data, "cost_current_wave1", answered_mask, num, cat)
    cost_noans = ts._oof_regression(data, target, ~answered_mask, num, cat)
    combined = (p_ans * cost_ans.fillna(0.0)
                + (1.0 - p_ans) * cost_noans.fillna(0.0))
    valid = combined.notna() & data[target].notna()
    y = data.loc[valid, target].astype(float).values
    pred2 = combined[valid].values
    report["two_stage"] = {
        "n": int(len(y)),
        "mae": float(mean_absolute_error(y, pred2)),
        "r2": float(r2_score(y, pred2)),
        "spearman": ts._spearman(y, pred2),
        "bootstrap_mae_ci": ts._bootstrap_regression(y, pred2)["mae_ci"],
    }
    print("two-stage", report["two_stage"], flush=True)

    # Impossible and correct classifiers.
    for target_name, model_name in (
        ("is_impossible_dir", "impossible_model.joblib"),
        ("correct_current_rate", "correct_model.joblib"),
    ):
        data = df.dropna(subset=[target_name]).copy()
        if target_name == "correct_current_rate":
            y = (data[target_name] >= 0.5).astype(int)
        else:
            y = data[target_name].astype(int)
        pipe = Pipeline([
            ("pre", ts._pre(num, cat)),
            ("model", RandomForestClassifier(
                n_estimators=400, min_samples_leaf=3, random_state=0, n_jobs=1)),
        ])
        pipe.fit(data[num + cat], y)
        joblib.dump(pipe, EXP / "results" / model_name)
        print("fitted", model_name, flush=True)

    (EXP / "results" / "predictor.json").write_text(json.dumps({
        "features": num + cat,
        "numeric": num,
        "categorical": cat,
        "cost_target": "log1p(mean total cost, current harness v0003)",
        "cost_model": "RandomForestRegressor(n_estimators=400, min_samples_leaf=3)",
        "impossible_model": "RandomForestClassifier(n_estimators=400, min_samples_leaf=3)",
        "correct_model": "RandomForestClassifier(n_estimators=400, min_samples_leaf=3)",
        "two_stage": {
            "answered_model": "answered_model.joblib",
            "cost_answered_model": "cost_answered_model.joblib",
            "cost_unanswered_model": "cost_unanswered_model.joblib",
            "formula": "P(answer) * E[wave1_cost | answer] + (1 - P(answer)) * E[total_cost | no answer]",
        },
        "trained_tasks": int(len(cost_data)),
        "caveat": "Absolute cost is harness-version specific; recalibrate.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (EXP / "results" / "static_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote static_report.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
