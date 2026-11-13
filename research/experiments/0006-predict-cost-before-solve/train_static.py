#!/usr/bin/env python3
"""Train and evaluate pre-solve cost and solvability predictors.

The predictor uses only static features (instruction, workspace, category,
reward).  Costs come from three sources:

* fresh ``0003`` runs (``results/current_runs.csv``), the primary target;
* the historical ``harness_v_0001.tsv``, for version transfer;
* ``exp0002`` first-wave costs, for version transfer.

Splits are by task.  The important checks are leave-one-category-out and
leave-one-id-block-out, because a random split over a synthetic generator
overstates transfer.

Usage::

    harness/.venv/bin/python \
        research/experiments/0006-predict-cost-before-solve/train_static.py
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import warnings
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold, KFold, LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[3]
warnings.filterwarnings("ignore")

EXCLUDE = {"rel", "task_id", "label", "is_impossible_dir", "task_type",
           "cost_current_mean", "cost_current_median", "cost_current_wave1",
           "cost_current_wave2",
           "correct_current_rate", "answered_current_rate", "n_current", "cost_v1_median",
           "cost_v1_mean", "correct_v1_rate", "n_v1", "cost_exp0002",
           "correct_exp0002", "cost_example_mean", "correct_example_rate",
           "n_example", "block", "split"}


def _spearman(a: Any, b: Any) -> float:
    value = spearmanr(a, b).correlation
    if value is None or not math.isfinite(float(value)):
        return 0.0
    return float(value)


def _ece(y: np.ndarray, pred: np.ndarray, bins: int = 10) -> float:
    y = np.asarray(y, dtype=float)
    pred = np.asarray(pred, dtype=float)
    edges = np.linspace(0.0, 1.0, bins + 1)
    total = 0.0
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (pred >= low) & (pred < high if high < 1.0 else pred <= high)
        if mask.sum() == 0:
            continue
        total += mask.mean() * abs(y[mask].mean() - pred[mask].mean())
    return float(total)


def _task_number(task_id: str) -> int:
    try:
        return int(str(task_id).split("_")[-1])
    except (ValueError, IndexError):
        return 0


def _block(task_id: str) -> str:
    n = _task_number(task_id)
    if n <= 10:
        return "A_0001_0010"
    if n <= 100:
        return "B_0011_0100"
    if n <= 200:
        return "C_0101_0200"
    if n <= 300:
        return "D_0201_0300"
    return "E_0301_0400"


def _load_targets(args: argparse.Namespace, tasks: pd.DataFrame) -> pd.DataFrame:
    df = tasks.copy()
    overview_path = getattr(args, "overview", None)
    if overview_path is not None and Path(overview_path).is_file():
        overview = pd.read_csv(overview_path)
        df = df.merge(overview, on="rel", how="left")
    # Fresh 0003 runs.
    if args.current_runs.is_file():
        runs = pd.read_csv(args.current_runs)
        if "answered_wave1" not in runs:
            runs["answered_wave1"] = (runs["turns"] == 1).astype(int)
        agg = runs.groupby("rel").agg(
            cost_current_mean=("cost", "mean"),
            cost_current_median=("cost", "median"),
            cost_current_wave1=("wave1_cost", "mean"),
            cost_current_wave2=("wave2_cost", "mean"),
            correct_current_rate=("correct", "mean"),
            answered_current_rate=("answered_wave1", "mean"),
            n_current=("cost", "size"),
        )
        df = df.merge(agg, left_on="rel", right_index=True, how="left")
    # v0001.
    v1 = pd.read_csv(args.v0001, sep="\t")
    v1["solved_bool"] = v1["is_solved_correctly"].astype(str).str.lower().eq("true")
    agg = v1.groupby("task_id").agg(
        cost_v1_median=("cost_tokens", "median"),
        cost_v1_mean=("cost_tokens", "mean"),
        correct_v1_rate=("solved_bool", "mean"),
        n_v1=("cost_tokens", "size"),
    )
    df = df.merge(agg, left_on="rel", right_index=True, how="left")
    # exp0002 (one wave).
    exp_paths = sorted((ROOT / "data" / "trajectories").glob(
        "exp0002-shard*/bash_attempts.jsonl"))
    if exp_paths:
        id_to_rel = dict(zip(df["task_id"], df["rel"]))
        rows = []
        for path in exp_paths:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rows.append(json.loads(line))
        cost = {}
        for record in rows:
            rel = id_to_rel.get(record["task_id"])
            if rel is None:
                continue
            value = int(record["output_tokens"]) + math.ceil(
                int(record["input_tokens"]) / 10)
            cost[rel] = cost.get(rel, 0) + value
        correctness_file = (ROOT / "research" / "experiments"
                            / "0002-first-wave-predictors" / "results"
                            / "correctness.json")
        correctness = json.loads(correctness_file.read_text(encoding="utf-8"))
        rows = []
        for rel, value in cost.items():
            task_id = df.loc[df["rel"] == rel, "task_id"]
            tid = task_id.iloc[0] if len(task_id) else ""
            rows.append({"rel": rel, "cost_exp0002": value,
                         "correct_exp0002": float(correctness.get(tid, False))})
        if rows:
            df = df.merge(pd.DataFrame(rows), on="rel", how="left")
    # Organizer examples (run separately).
    if args.examples_runs.is_file():
        runs = pd.read_csv(args.examples_runs)
        agg = runs.groupby("rel").agg(
            cost_example_mean=("cost", "mean"),
            correct_example_rate=("correct", "mean"),
            n_example=("cost", "size"),
        )
        df = df.merge(agg, left_on="rel", right_index=True, how="left")
    df["block"] = df["task_id"].map(_block)
    return df


def _features(df: pd.DataFrame, leak: bool = False) -> tuple[list[str], list[str]]:
    num = [c for c in df.columns
           if c not in EXCLUDE and pd.api.types.is_numeric_dtype(df[c])]
    cat = ["task_type"]
    if leak:
        for column in ("check",):
            if column in df.columns:
                cat.append(column)
        for column in ("has_expected", "has_solvable_field"):
            if column in df.columns and column not in num:
                num.append(column)
    return num, cat


def _pre(num: list[str], cat: list[str]) -> ColumnTransformer:
    return ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                          ("scale", StandardScaler())]), num),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat),
    ])


def _regressors() -> dict[str, Callable[[], Any]]:
    return {
        "ridge": lambda: Ridge(alpha=10.0),
        "rf": lambda: RandomForestRegressor(
            n_estimators=300, min_samples_leaf=3, random_state=0, n_jobs=1),
        "hgb": lambda: HistGradientBoostingRegressor(
            max_iter=200, learning_rate=0.05, random_state=0),
    }


def _classifiers() -> dict[str, Callable[[], Any]]:
    return {
        "logreg": lambda: LogisticRegression(max_iter=3000, C=1.0),
        "rf": lambda: RandomForestClassifier(
            n_estimators=300, min_samples_leaf=3, random_state=0, n_jobs=1),
        "hgb": lambda: HistGradientBoostingClassifier(
            max_iter=200, learning_rate=0.05, random_state=0),
    }


def _splitter(mode: str, df: pd.DataFrame, n_splits: int = 5):
    if mode == "category":
        return LeaveOneGroupOut(), df["task_type"]
    if mode == "block":
        return LeaveOneGroupOut(), df["block"]
    return GroupKFold(n_splits=n_splits), df["task_id"]


def _regression_cv(
    df: pd.DataFrame,
    target: str,
    num: list[str],
    cat: list[str],
    mode: str,
    model_factory: Callable[[], Any],
) -> tuple[np.ndarray, dict[str, Any]]:
    data = df.dropna(subset=[target]).copy()
    y = data[target].astype(float).values
    log_y = np.log1p(y)
    pred = np.zeros(len(data))
    splitter, groups = _splitter(mode, data)
    for train_idx, test_idx in splitter.split(data, log_y, groups=groups):
        pipe = Pipeline([("pre", _pre(num, cat)), ("model", model_factory())])
        pipe.fit(data.iloc[train_idx][num + cat], log_y[train_idx])
        fold = np.expm1(pipe.predict(data.iloc[test_idx][num + cat]))
        low, high = np.percentile(y[train_idx], [1, 99])
        pred[test_idx] = np.clip(fold, max(1.0, low), high)
    metrics = {
        "n": int(len(data)),
        "mae": float(mean_absolute_error(y, pred)),
        "medae": float(np.median(np.abs(y - pred))),
        "rmse": float(mean_squared_error(y, pred) ** 0.5),
        "r2": float(r2_score(y, pred)),
        "spearman": float(_spearman(y, pred)),
        "mape": float(np.mean(np.abs(y - pred) / np.maximum(1.0, y))),
    }
    return pred, metrics


def _category_median_baseline(df: pd.DataFrame, target: str, mode: str) -> dict[str, float]:
    data = df.dropna(subset=[target]).copy()
    y = data[target].astype(float).values
    pred = np.zeros(len(data))
    splitter, groups = _splitter(mode, data)
    for train_idx, test_idx in splitter.split(data, y, groups=groups):
        train = data.iloc[train_idx]
        fallback = float(np.median(train[target]))
        medians = train.groupby("task_type")[target].median().to_dict()
        pred[test_idx] = [medians.get(cat, fallback)
                          for cat in data.iloc[test_idx]["task_type"]]
    return {
        "mae": float(mean_absolute_error(y, pred)),
        "r2": float(r2_score(y, pred)),
        "spearman": float(_spearman(y, pred)),
    }


def _classification_cv(
    df: pd.DataFrame,
    target: str,
    num: list[str],
    cat: list[str],
    mode: str,
    model_factory: Callable[[], Any],
) -> tuple[np.ndarray, dict[str, Any]]:
    data = df.dropna(subset=[target]).copy()
    y = data[target].astype(int).values
    pred = np.zeros(len(data))
    splitter, groups = _splitter(mode, data)
    for train_idx, test_idx in splitter.split(data, y, groups=groups):
        pipe = Pipeline([("pre", _pre(num, cat)), ("model", model_factory())])
        pipe.fit(data.iloc[train_idx][num + cat], y[train_idx])
        pred[test_idx] = pipe.predict_proba(data.iloc[test_idx][num + cat])[:, 1]
    return pred, {
        "n": int(len(data)),
        "auc": float(roc_auc_score(y, pred)),
        "pr_auc": float(average_precision_score(y, pred)),
        "brier": float(brier_score_loss(y, pred)),
        "ece": _ece(y, pred),
        "accuracy": float(((pred >= 0.5) == y).mean()),
        "base_rate": float(y.mean()),
    }


def _bootstrap_regression(
    y: np.ndarray, pred: np.ndarray, n: int = 300, seed: int = 0
) -> dict[str, list[float]]:
    rng = np.random.default_rng(seed)
    maes, rhos = [], []
    for _ in range(n):
        idx = rng.integers(0, len(y), len(y))
        maes.append(mean_absolute_error(y[idx], pred[idx]))
        rho = _spearman(y[idx], pred[idx])
        if rho is not None:
            rhos.append(float(rho))
    return {
        "mae_ci": [float(np.percentile(maes, 2.5)), float(np.percentile(maes, 97.5))],
        "spearman_ci": [float(np.percentile(rhos, 2.5)), float(np.percentile(rhos, 97.5))],
    }


def _oof_regression(
    df: pd.DataFrame,
    target: str,
    subset: pd.Series,
    num: list[str],
    cat: list[str],
    mode: str = "random",
) -> pd.Series:
    data = df[subset].dropna(subset=[target]).copy()
    result = pd.Series(np.nan, index=df.index, dtype=float)
    if len(data) < 5:
        return result
    splitter, groups = _splitter(mode, data)
    for train_idx, test_idx in splitter.split(data, data[target], groups=groups):
        pipe = Pipeline([("pre", _pre(num, cat)),
                         ("model", HistGradientBoostingRegressor(
                             max_iter=200, learning_rate=0.05, random_state=0))])
        pipe.fit(data.iloc[train_idx][num + cat],
                 np.log1p(data.iloc[train_idx][target].astype(float)))
        fold = np.expm1(pipe.predict(data.iloc[test_idx][num + cat]))
        low, high = np.percentile(data.iloc[train_idx][target], [1, 99])
        result.loc[data.index[test_idx]] = np.clip(
            fold, max(1.0, low), high)
    return result


def _oof_classifier(
    df: pd.DataFrame,
    target: str,
    num: list[str],
    cat: list[str],
    mode: str = "random",
) -> pd.Series:
    data = df.dropna(subset=[target]).copy()
    y = data[target].astype(int).values
    result = pd.Series(np.nan, index=df.index, dtype=float)
    splitter, groups = _splitter(mode, data)
    for train_idx, test_idx in splitter.split(data, y, groups=groups):
        pipe = Pipeline([("pre", _pre(num, cat)),
                         ("model", RandomForestClassifier(
                             n_estimators=300, min_samples_leaf=3,
                             random_state=0, n_jobs=1))])
        pipe.fit(data.iloc[train_idx][num + cat], y[train_idx])
        result.loc[data.index[test_idx]] = pipe.predict_proba(
            data.iloc[test_idx][num + cat])[:, 1]
    return result


def _write_predictor(df: pd.DataFrame, num: list[str], cat: list[str], out: Path) -> None:
    """Fit the final models on all labelled tasks and save a bundle."""
    import joblib

    if "cost_current_mean" not in df or df["cost_current_mean"].notna().sum() < 20:
        print("skip predictor bundle: no current-cost target yet")
        return
    cost_data = df.dropna(subset=["cost_current_mean"]).copy()
    cost_y = np.log1p(cost_data["cost_current_mean"].astype(float).values)
    cost_pipe = Pipeline([
        ("pre", _pre(num, cat)),
        ("model", RandomForestRegressor(
            n_estimators=400, min_samples_leaf=3, random_state=0, n_jobs=1)),
    ])
    cost_pipe.fit(cost_data[num + cat], cost_y)
    joblib.dump(cost_pipe, out / "cost_model.joblib")

    # Dependency-free linear export: the same features, median imputation,
    # standardisation and one-hot categories as explicit JSON.
    linear = Pipeline([
        ("pre", _pre(num, cat)),
        ("model", Ridge(alpha=10.0)),
    ])
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
    (out / "linear_cost_model.json").write_text(
        json.dumps(linear_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    solv_y = cost_data["is_impossible_dir"].astype(int).values
    solv_pipe = Pipeline([
        ("pre", _pre(num, cat)),
        ("model", RandomForestClassifier(
            n_estimators=400, min_samples_leaf=3, random_state=0, n_jobs=1)),
    ])
    solv_pipe.fit(cost_data[num + cat], solv_y)
    joblib.dump(solv_pipe, out / "impossible_model.joblib")

    if ("correct_current_rate" in cost_data
            and cost_data["correct_current_rate"].notna().sum() >= 20):
        correct_y = (cost_data["correct_current_rate"] >= 0.5).astype(int).values
        correct_pipe = Pipeline([
            ("pre", _pre(num, cat)),
            ("model", RandomForestClassifier(
                n_estimators=400, min_samples_leaf=3, random_state=0, n_jobs=1)),
        ])
        correct_pipe.fit(cost_data[num + cat], correct_y)
        joblib.dump(correct_pipe, out / "correct_model.joblib")
    (out / "predictor.json").write_text(json.dumps({
        "features": num + cat,
        "numeric": num,
        "categorical": cat,
        "cost_target": "log1p(mean total cost, current harness v0003)",
        "cost_model": "RandomForestRegressor(n_estimators=400, min_samples_leaf=3)",
        "impossible_model": "RandomForestClassifier(n_estimators=400, min_samples_leaf=3)",
        "correct_model": "RandomForestClassifier(n_estimators=400, min_samples_leaf=3)",
        "trained_tasks": int(len(cost_data)),
        "caveat": "Absolute cost is harness-version specific; recalibrate on new runs.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    parser.add_argument("--features", type=Path,
                        default=here / "results" / "static_features.csv")
    parser.add_argument("--leak-features", type=Path,
                        default=here / "results" / "static_features_leak.csv")
    parser.add_argument("--current-runs", type=Path,
                        default=here / "results" / "current_runs.csv")
    parser.add_argument("--examples-runs", type=Path,
                        default=here / "results" / "example_runs.csv")
    parser.add_argument("--overview", type=Path,
                        default=here / "results" / "overview_features.csv")
    parser.add_argument("--v0001", type=Path,
                        default=ROOT / "data" / "harness_task_score" / "harness_v_0001.tsv")
    parser.add_argument("--out-dir", type=Path, default=here / "results")
    args = parser.parse_args(argv)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    tasks = pd.read_csv(args.features)
    df = _load_targets(args, tasks)
    num, cat = _features(df)
    print(f"tasks: {len(df)}; numeric features: {len(num)}; cat: {cat}")
    print("targets available:",
          {target: int(df[target].notna().sum()) if target in df else 0
           for target in ("cost_current_mean", "cost_v1_median", "cost_exp0002")})
    report: dict[str, Any] = {"tasks": len(df), "features": num + cat}

    targets = [
        ("cost_current_mean", "current v0003"),
        ("cost_v1_median", "v0001"),
        ("cost_exp0002", "exp0002 wave1"),
    ]
    report["regression"] = {}
    for target, label in targets:
        if target not in df or df[target].notna().sum() < 20:
            continue
        print(f"\n== cost: {label} ==")
        target_report: dict[str, Any] = {}
        for mode in ("random", "category", "block"):
            base = _category_median_baseline(df, target, mode)
            print(f"{mode:9s} category-median MAE={base['mae']:7.1f} "
                  f"rho={base['spearman']:.3f}")
            target_report[f"baseline_category_{mode}"] = base
            for name, factory in _regressors().items():
                _, metrics = _regression_cv(df, target, num, cat, mode, factory)
                target_report[f"{name}_{mode}"] = metrics
                print(f"{mode:9s} {name:6s} MAE={metrics['mae']:7.1f} "
                      f"R2={metrics['r2']:6.3f} rho={metrics['spearman']:.3f}")
        # Bootstrap for the best random-split model.
        best_name = max(
            ("ridge", "rf", "hgb"),
            key=lambda name: target_report[f"{name}_random"]["spearman"],
        )
        data = df.dropna(subset=[target])
        pred, _ = _regression_cv(df, target, num, cat, "random",
                                 _regressors()[best_name])
        y = data[target].astype(float).values
        target_report["bootstrap_best"] = _bootstrap_regression(y, pred)
        target_report["best_random_model"] = best_name
        report["regression"][target] = target_report
        if target == "cost_current_mean":
            pd.DataFrame({
                "rel": data["rel"].values,
                "task_type": data["task_type"].values,
                "impossible": data["is_impossible_dir"].values,
                "actual": y,
                "predicted": pred,
            }).to_csv(args.out_dir / "static_predictions.csv", index=False)

    # Cross-version transfer: rank correlation between predictions from
    # v0001-trained model and actual current cost.
    if ("cost_v1_median" in df and "cost_current_mean" in df
            and df["cost_v1_median"].notna().sum() > 20):
        mask = df["cost_v1_median"].notna() & df["cost_current_mean"].notna()
        data = df[mask].copy()
        pred_v1, _ = _regression_cv(
            data, "cost_v1_median", num, cat, "random", _regressors()["hgb"])
        pred_cur, _ = _regression_cv(
            data, "cost_current_mean", num, cat, "random", _regressors()["hgb"])
        report["cross_version"] = {
            "n": int(len(data)),
            "spearman_pred_v1_vs_pred_current": float(
                _spearman(pred_v1, pred_cur)),
            "spearman_actual_v1_vs_actual_current": float(
                _spearman(data["cost_v1_median"], data["cost_current_mean"])),
        }
        print("\ncross-version", report["cross_version"])

    # Solvability: honest vs leak.
    print("\n== solvability ==")
    report["solvability"] = {}
    for mode in ("random", "category", "block"):
        for name, factory in _classifiers().items():
            _, metrics = _classification_cv(
                df, "is_impossible_dir", num, cat, mode, factory)
            report["solvability"][f"honest_{name}_{mode}"] = metrics
            print(f"honest {mode:9s} {name:6s} AUC={metrics['auc']:.3f} "
                  f"PR={metrics['pr_auc']:.3f}")
    if args.leak_features.is_file():
        leak = pd.read_csv(args.leak_features)
        leak_num, leak_cat = _features(leak, leak=True)
        leak = _load_targets(args, leak)
        print("leak columns:", leak_cat, [c for c in leak_num if c.startswith("has_")])
        for mode in ("random", "category", "block"):
            _, metrics = _classification_cv(
                leak, "is_impossible_dir", leak_num, leak_cat, mode,
                _classifiers()["rf"])
            report["solvability"][f"leak_rf_{mode}"] = metrics
            print(f"leak   {mode:9s} rf     AUC={metrics['auc']:.3f} "
                  f"PR={metrics['pr_auc']:.3f}")

    # Two-stage current-cost model: P(answer in wave 1), cost when answered,
    # total cost when not answered.
    if ("cost_current_mean" in df and "answered_current_rate" in df
            and df["cost_current_mean"].notna().sum() >= 20):
        print("\n== two-stage current cost ==")
        data = df.dropna(subset=["cost_current_mean", "answered_current_rate",
                                 "cost_current_wave1"]).copy()
        data["answered_any"] = (data["answered_current_rate"] >= 0.5).astype(int)
        p_ans = _oof_classifier(data, "answered_any", num, cat)
        answered_mask = data["answered_any"] == 1
        cost_answered = _oof_regression(
            data, "cost_current_wave1", answered_mask, num, cat)
        cost_unanswered = _oof_regression(
            data, "cost_current_mean", ~answered_mask, num, cat)
        combined = (p_ans * cost_answered.fillna(0.0)
                    + (1.0 - p_ans) * cost_unanswered.fillna(0.0))
        valid = combined.notna() & data["cost_current_mean"].notna()
        y = data.loc[valid, "cost_current_mean"].astype(float).values
        pred = combined[valid].values
        metrics = {
            "n": int(valid.sum()),
            "mae": float(mean_absolute_error(y, pred)),
            "r2": float(r2_score(y, pred)),
            "spearman": _spearman(y, pred),
            "mae_bootstrap_ci": _bootstrap_regression(y, pred)["mae_ci"],
        }
        report["two_stage_current_cost"] = metrics
        print("two-stage", metrics)
        # Direct model on the same rows for a fair comparison.
        _, direct = _regression_cv(
            data, "cost_current_mean", num, cat, "random", _regressors()["hgb"])
        report["two_stage_direct_baseline"] = direct
        print("direct   ", direct)

    # Will the task be solved correctly?  This is the pre-solve version of
    # "can the agent do this task", independent of the impossible label.
    if ("correct_current_rate" in df
            and df["correct_current_rate"].notna().sum() >= 20):
        print("\n== solved correctly ==")
        data = df.dropna(subset=["correct_current_rate"]).copy()
        data["solved_any"] = (data["correct_current_rate"] >= 0.5).astype(int)
        report["solved_correctly"] = {}
        for mode in ("random", "category", "block"):
            for name, factory in _classifiers().items():
                splits, groups = _splitter(mode, data)
                pred = np.zeros(len(data))
                for tr, te in splits.split(data, data["solved_any"], groups=groups):
                    pipe = Pipeline([("pre", _pre(num, cat)), ("model", factory())])
                    pipe.fit(data.iloc[tr][num + cat], data.iloc[tr]["solved_any"])
                    pred[te] = pipe.predict_proba(data.iloc[te][num + cat])[:, 1]
                metrics = {
                    "n": int(len(data)),
                    "auc": float(roc_auc_score(data["solved_any"], pred)),
                    "pr_auc": float(average_precision_score(
                        data["solved_any"], pred)),
                    "base_rate": float(data["solved_any"].mean()),
                }
                report["solved_correctly"][f"{name}_{mode}"] = metrics
                print(f"{mode:9s} {name:6s} AUC={metrics['auc']:.3f} "
                      f"PR={metrics['pr_auc']:.3f} base={metrics['base_rate']:.3f}")

    # Will the task be answered in one turn?  With wave2_max_tasks=0 the
    # harness runs a second turn exactly when wave 1 produced no answer, so
    # this is the pre-solve version of "expected number of turns".
    if "answered_current_rate" in df and df["answered_current_rate"].notna().sum() >= 20:
        print("\n== answered in wave 1 ==")
        data = df.dropna(subset=["answered_current_rate"]).copy()
        data["answered_any"] = (data["answered_current_rate"] >= 0.5).astype(int)
        report["answered_wave1"] = {}
        for mode in ("random", "category", "block"):
            splits, groups = _splitter(mode, data)
            pred = np.zeros(len(data))
            for tr, te in splits.split(data, data["answered_any"], groups=groups):
                pipe = Pipeline([("pre", _pre(num, cat)),
                                 ("model", RandomForestClassifier(
                                     n_estimators=300, min_samples_leaf=3,
                                     random_state=0, n_jobs=1))])
                pipe.fit(data.iloc[tr][num + cat], data.iloc[tr]["answered_any"])
                pred[te] = pipe.predict_proba(data.iloc[te][num + cat])[:, 1]
            metrics = {
                "n": int(len(data)),
                "auc": float(roc_auc_score(data["answered_any"], pred)),
                "pr_auc": float(average_precision_score(
                    data["answered_any"], pred)),
                "base_rate": float(data["answered_any"].mean()),
            }
            report["answered_wave1"][f"rf_{mode}"] = metrics
            print(f"{mode:9s} rf AUC={metrics['auc']:.3f} "
                  f"PR={metrics['pr_auc']:.3f} base={metrics['base_rate']:.3f}")

    # External organizer examples: train without the eight example tasks.
    example_mask = (df["cost_example_mean"].notna()
                    if "cost_example_mean" in df else pd.Series(False, index=df.index))
    if example_mask.sum() >= 4:
        train = df[~example_mask]
        test = df[example_mask]
        # Fit on all non-example tasks, predict the eight example costs.
        pipe = Pipeline([
            ("pre", _pre(num, cat)),
            ("model", RandomForestRegressor(
                n_estimators=300, min_samples_leaf=3, random_state=0, n_jobs=1)),
        ])
        pipe.fit(train[num + cat],
                 np.log1p(train["cost_current_mean"].astype(float)))
        pred = np.expm1(pipe.predict(test[num + cat]))
        actual = test["cost_example_mean"].astype(float).values
        external = {
            "n": int(len(test)),
            "spearman": float(_spearman(actual, pred)),
            "mae": float(mean_absolute_error(actual, pred)),
            "actual": actual.tolist(),
            "predicted": pred.tolist(),
        }
        report["external_examples"] = external
        print("\nexternal examples", external)

    # Feature importance on the current cost target.
    if "cost_current_mean" in df and df["cost_current_mean"].notna().sum() >= 20:
        data = df.dropna(subset=["cost_current_mean"])
        pipe = Pipeline([
            ("pre", _pre(num, cat)),
            ("model", RandomForestRegressor(
                n_estimators=300, min_samples_leaf=3, random_state=0, n_jobs=1)),
        ])
        y = np.log1p(data["cost_current_mean"].astype(float))
        pipe.fit(data[num + cat], y)
        importance = permutation_importance(
            pipe, data[num + cat], y, n_repeats=5, random_state=0,
            scoring="neg_mean_absolute_error", n_jobs=1,
        )
        order = np.argsort(importance.importances_mean)[::-1][:20]
        report["importance"] = [
            {"feature": (num + cat)[i],
             "importance": float(importance.importances_mean[i])}
            for i in order
        ]
        print("\ntop features:", [item["feature"] for item in report["importance"][:10]])

    _write_predictor(df, num, cat, args.out_dir)
    (args.out_dir / "static_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {args.out_dir / 'static_report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
