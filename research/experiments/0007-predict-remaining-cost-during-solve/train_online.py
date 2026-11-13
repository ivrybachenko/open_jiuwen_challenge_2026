#!/usr/bin/env python3
"""Train and evaluate online (after-first-turn) cost and success predictors.

Targets:

* next-turn input tokens, output tokens and cost (from ``turn_pairs.csv``);
* remaining cost after the first turn and total task cost
  (from ``turn_groups.csv``);
* probability that the submitted answer is correct;
* probability that the task is impossible;
* an offline wave-2 selection rule.

Everything is grouped by task: several repeats of one task never appear in both
train and test.

Usage::

    harness/.venv/bin/python \
        research/experiments/0007-predict-remaining-cost-during-solve/train_online.py \
        --out-dir research/experiments/0007-predict-remaining-cost-during-solve/results
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
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.application.features import promise_score  # noqa: E402

warnings.filterwarnings("ignore")

CAT_COLS = ["task_type", "answer_kind"]

GROUP_NUM = [
    "reward", "input_tokens", "output_tokens", "cost", "reasoning_chars",
    "reasoning_words", "output_chars", "output_lines", "script_chars",
    "script_lines", "script_words", "answer_chars", "overview_chars",
    "overview_lines", "hit_token_limit", "timed_out", "tests_in_overview",
    "reasoning_keyword_impossible", "reasoning_keyword_give_up",
    "script_has_python", "script_has_tests", "script_has_file_ops",
    "script_has_write_answer", "script_mentions_impossible", "answer_present",
    "answer_impossible", "exit_bad", "n_cat", "n_grep", "n_find", "n_ls",
    "n_head", "n_tail", "n_awk", "n_sed", "n_sort", "n_wc", "n_python",
    "n_test", "n_for", "n_while", "n_if", "n_pipe", "n_semicolon",
    "n_redirect", "n_echo", "n_impossible",
]

PAIR_NUM = [
    "prev_input", "prev_output", "prev_cost", "exec_chars", "exec_lines",
    "script_chars", "hit_token_limit", "prev_exit_bad",
]


def _preprocessor(num: list[str], cat: list[str]) -> ColumnTransformer:
    return ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                          ("scale", StandardScaler())]), num),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat),
    ])


def _regressors() -> dict[str, Callable[[], Any]]:
    return {
        "ridge": lambda: Ridge(alpha=10.0),
        "rf": lambda: RandomForestRegressor(
            n_estimators=300, min_samples_leaf=3, random_state=0, n_jobs=1
        ),
        "hgb": lambda: HistGradientBoostingRegressor(
            max_iter=200, learning_rate=0.05, random_state=0
        ),
    }


def _classifiers() -> dict[str, Callable[[], Any]]:
    return {
        "logreg": lambda: LogisticRegression(max_iter=3000, C=1.0),
        "rf": lambda: RandomForestClassifier(
            n_estimators=300, min_samples_leaf=3, random_state=0, n_jobs=1
        ),
        "hgb": lambda: HistGradientBoostingClassifier(
            max_iter=200, learning_rate=0.05, random_state=0
        ),
    }


def _cv_regression(
    df: pd.DataFrame,
    target: str,
    num: list[str],
    cat: list[str],
    model_factory: Callable[[], Any],
    groups: str = "task_id",
    splitter: Any | None = None,
) -> tuple[np.ndarray, dict[str, float]]:
    y = df[target].astype(float).values
    pred = np.zeros(len(df))
    splitter = splitter or GroupKFold(n_splits=5)
    for train_idx, test_idx in splitter.split(df, y, groups=df[groups]):
        pipe = Pipeline([
            ("pre", _preprocessor(num, cat)),
            ("model", model_factory()),
        ])
        pipe.fit(df.iloc[train_idx][num + cat], y[train_idx])
        pred[test_idx] = pipe.predict(df.iloc[test_idx][num + cat])
    metrics = {
        "mae": float(mean_absolute_error(y, pred)),
        "medae": float(np.median(np.abs(y - pred))),
        "rmse": float(mean_squared_error(y, pred) ** 0.5),
        "r2": float(r2_score(y, pred)),
        "spearman": float(spearmanr(y, pred).correlation or 0.0),
        "mape": float(np.mean(np.abs(y - pred) / np.maximum(1.0, np.abs(y)))),
    }
    return pred, metrics


def _cv_classification(
    df: pd.DataFrame,
    target: str,
    num: list[str],
    cat: list[str],
    model_factory: Callable[[], Any],
    groups: str = "task_id",
    splitter: Any | None = None,
) -> tuple[np.ndarray, dict[str, float]]:
    y = df[target].astype(int).values
    pred = np.zeros(len(df))
    splitter = splitter or GroupKFold(n_splits=5)
    for train_idx, test_idx in splitter.split(df, y, groups=df[groups]):
        pipe = Pipeline([
            ("pre", _preprocessor(num, cat)),
            ("model", model_factory()),
        ])
        pipe.fit(df.iloc[train_idx][num + cat], y[train_idx])
        pred[test_idx] = pipe.predict_proba(df.iloc[test_idx][num + cat])[:, 1]
    metrics = {
        "auc": float(roc_auc_score(y, pred)),
        "pr_auc": float(average_precision_score(y, pred)),
        "brier": float(brier_score_loss(y, pred)),
        "log_loss": float(log_loss(y, np.clip(pred, 1e-6, 1 - 1e-6))),
        "accuracy": float(((pred >= 0.5) == y).mean()),
        "ece": _ece(y, pred),
        "base_rate": float(y.mean()),
    }
    return pred, metrics


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


def _bootstrap_metric(
    y: np.ndarray, pred: np.ndarray, metric: Callable[[np.ndarray, np.ndarray], float],
    n: int = 300, seed: int = 0,
) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(n):
        idx = rng.integers(0, len(y), len(y))
        if len(np.unique(y[idx])) < 2:
            continue
        values.append(metric(y[idx], pred[idx]))
    if not values:
        return float("nan"), float("nan"), float("nan")
    return (float(metric(y, pred)), float(np.percentile(values, 2.5)),
            float(np.percentile(values, 97.5)))


def _selection_simulation(
    df: pd.DataFrame,
    probability: np.ndarray,
    predicted_remaining: np.ndarray,
    lambdas: list[float],
) -> list[dict[str, Any]]:
    """Counterfactual wave-2 policy on tasks that were not answered in wave 1.

    The logged run already contains the actual wave-2 outcome.  If the policy
    skips wave 2, the task scores zero and costs only wave 1.  If it runs
    wave 2, the task costs the logged total and scores the logged correctness.
    """
    results = []
    candidates = df[df["answered"] == 0].copy()
    prob = probability[df["answered"].to_numpy() == 0]
    pred_cost = predicted_remaining[df["answered"].to_numpy() == 0]
    for lam in lambdas:
        score = 0.0
        cost = 0.0
        ran = 0
        for i, (_, row) in enumerate(candidates.iterrows()):
            base_cost = float(row["cost"])
            if prob[i] * float(row["reward"]) > lam * max(1.0, pred_cost[i]):
                ran += 1
                cost += float(row["total_cost"])
                score += float(row["reward"]) * float(row["correct"])
            else:
                cost += base_cost
        results.append({
            "lambda": lam,
            "ran": ran,
            "score": score,
            "cost": cost,
            "score_per_1k": 1000.0 * score / max(1.0, cost),
        })
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--groups", type=Path,
                        default=Path(__file__).resolve().parent / "results" / "turn_groups.csv")
    parser.add_argument("--pairs", type=Path,
                        default=Path(__file__).resolve().parent / "results" / "turn_pairs.csv")
    parser.add_argument("--out-dir", type=Path,
                        default=Path(__file__).resolve().parent / "results")
    args = parser.parse_args(argv)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    groups = pd.read_csv(args.groups)
    pairs = pd.read_csv(args.pairs)
    groups = groups[groups["has_correctness"] == 1].copy()
    print(f"groups: {len(groups)}; tasks: {groups.task_id.nunique()}")
    print(groups.groupby("source").size().to_string())

    report: dict[str, Any] = {"groups": len(groups),
                              "tasks": int(groups.task_id.nunique()),
                              "pairs": len(pairs)}

    # ------------------------------------------------------------------
    # 1. Next-turn input / output / cost
    # ------------------------------------------------------------------
    print("\n== next turn cost ==")
    pairs = pairs.copy()
    pairs["input_formula"] = (
        pairs["prev_input"] + pairs["prev_output"] + pairs["exec_chars"] / 4.0 + 154.0
    )
    for target in ["next_input", "next_output", "next_cost"]:
        y = pairs[target].astype(float).values
        baseline = np.full(len(y), np.median(y))
        print(f"-- {target}: median={np.median(y):.0f}, MAE(median)={mean_absolute_error(y, baseline):.0f}")
    pair_metrics = {}
    for target in ["next_input", "next_output", "next_cost"]:
        for name, factory in _regressors().items():
            _, metrics = _cv_regression(
                pairs, target, PAIR_NUM, CAT_COLS, factory,
                groups="task_id",
            )
            pair_metrics[f"{target}/{name}"] = metrics
            print(f"{target:12s} {name:6s} MAE={metrics['mae']:7.1f} "
                  f"MAPE={metrics['mape']:6.3f} R2={metrics['r2']:6.3f} "
                  f"rho={metrics['spearman']:6.3f}")
    # deterministic input baseline
    formula_mae = mean_absolute_error(pairs["next_input"], pairs["input_formula"])
    pair_metrics["next_input/formula"] = {
        "mae": float(formula_mae),
        "mape": float(np.mean(np.abs(pairs["next_input"] - pairs["input_formula"])
                              / np.maximum(1, pairs["next_input"]))),
    }
    print(f"next_input   formula MAE={formula_mae:7.1f}")
    # Simple rule: median next cost by wave-1 answer kind, fitted out of fold.
    rule_pred = np.zeros(len(pairs))
    splitter = GroupKFold(n_splits=5)
    for train_idx, test_idx in splitter.split(
            pairs, pairs["next_cost"], groups=pairs["task_id"]):
        train = pairs.iloc[train_idx]
        fallback = float(train["next_cost"].median())
        medians = train.groupby("answer_kind")["next_cost"].median().to_dict()
        rule_pred[test_idx] = [
            medians.get(kind, fallback)
            for kind in pairs.iloc[test_idx]["answer_kind"]
        ]
    pair_metrics["next_cost/answer_kind_rule"] = {
        "mae": float(mean_absolute_error(pairs["next_cost"], rule_pred)),
        "mape": float(np.mean(np.abs(pairs["next_cost"] - rule_pred)
                              / np.maximum(1, pairs["next_cost"]))),
    }
    print("next_cost   rule by answer_kind MAE=",
          round(pair_metrics["next_cost/answer_kind_rule"]["mae"], 1))
    report["next_turn"] = pair_metrics

    # ------------------------------------------------------------------
    # 2. Remaining and total cost
    # ------------------------------------------------------------------
    print("\n== remaining cost ==")
    unanswered = groups[groups["answered"] == 0].copy()
    print(f"unanswered: {len(unanswered)}")
    remaining_metrics = {}
    for name, factory in _regressors().items():
        _, metrics = _cv_regression(
            unanswered, "remaining_cost", GROUP_NUM, CAT_COLS, factory
        )
        remaining_metrics[name] = metrics
        print(f"remaining/{name:6s} MAE={metrics['mae']:7.1f} "
              f"R2={metrics['r2']:6.3f} rho={metrics['spearman']:6.3f}")
    median_remaining = np.median(unanswered["remaining_cost"])
    base_mae = mean_absolute_error(
        unanswered["remaining_cost"], np.full(len(unanswered), median_remaining)
    )
    remaining_metrics["median_baseline"] = {"mae": float(base_mae),
                                            "value": float(median_remaining)}
    print(f"remaining/median MAE={base_mae:7.1f} value={median_remaining:.0f}")
    # total cost for all tasks: cost1 + 0 if answered else predicted remainder
    _, total_metrics = _cv_regression(
        groups, "total_cost", GROUP_NUM, CAT_COLS,
        lambda: HistGradientBoostingRegressor(
            max_iter=200, learning_rate=0.05, random_state=0
        ),
    )
    print(f"total/hgb MAE={total_metrics['mae']:7.1f} R2={total_metrics['r2']:6.3f}")
    report["remaining"] = remaining_metrics
    report["total_cost_hgb"] = total_metrics

    # ------------------------------------------------------------------
    # 3. Correctness and impossibility after the first turn
    # ------------------------------------------------------------------
    print("\n== correctness ==")
    class_metrics: dict[str, Any] = {}
    for target in ["correct", "impossible_label"]:
        print(f"-- {target}")
        for name, factory in _classifiers().items():
            _, metrics = _cv_classification(
                groups, target, GROUP_NUM, CAT_COLS, factory
            )
            class_metrics[f"{target}/{name}"] = metrics
            print(f"{target:16s} {name:6s} AUC={metrics['auc']:.3f} "
                  f"PR={metrics['pr_auc']:.3f} Brier={metrics['brier']:.3f} "
                  f"acc={metrics['accuracy']:.3f}")
        rule = groups["answer_present"].astype(float).values
        if target == "correct":
            rule_metrics = {
                "auc": float(roc_auc_score(groups[target], rule)),
                "accuracy": float(((rule >= 0.5) == groups[target]).mean()),
            }
            print(f"{target:16s} rule   AUC={rule_metrics['auc']:.3f} "
                  f"acc={rule_metrics['accuracy']:.3f}")
            class_metrics[f"{target}/answer_present_rule"] = rule_metrics
        if target == "impossible_label":
            rule2 = (
                (groups["answer_impossible"] == 1)
                | (groups["script_mentions_impossible"] == 1)
                | (groups["reasoning_keyword_impossible"] > 0)
            ).astype(float)
            rule_metrics = {
                "auc": float(roc_auc_score(groups[target], rule2)),
                "accuracy": float(((rule2 >= 0.5) == groups[target]).mean()),
            }
            print(f"{target:16s} rule   AUC={rule_metrics['auc']:.3f} "
                  f"acc={rule_metrics['accuracy']:.3f}")
            class_metrics[f"{target}/mention_rule"] = rule_metrics
    report["classification"] = class_metrics

    # ------------------------------------------------------------------
    # 4. Leave-one-category-out check for the main classifiers
    # ------------------------------------------------------------------
    print("\n== leave-one-category-out ==")
    loco: dict[str, Any] = {}
    splitter = LeaveOneGroupOut()
    for target in ["correct", "impossible_label"]:
        fold_rows = []
        for train_idx, test_idx in splitter.split(groups, groups=groups["task_type"]):
            train = groups.iloc[train_idx]
            test = groups.iloc[test_idx]
            pipe = Pipeline([
                ("pre", _preprocessor(GROUP_NUM, CAT_COLS)),
                ("model", RandomForestClassifier(
                    n_estimators=300, min_samples_leaf=3, random_state=0, n_jobs=1
                )),
            ])
            pipe.fit(train[GROUP_NUM + CAT_COLS], train[target])
            pred = pipe.predict_proba(test[GROUP_NUM + CAT_COLS])[:, 1]
            fold_rows.append({
                "test_category": test["task_type"].iloc[0],
                "n": len(test),
                "auc": float(roc_auc_score(test[target], pred))
                if test[target].nunique() > 1 else None,
            })
        loco[target] = fold_rows
        print(target, fold_rows)
    report["leave_one_category_out"] = loco

    # ------------------------------------------------------------------
    # 5. Offline wave-2 selection rule
    # ------------------------------------------------------------------
    print("\n== selection ==")
    # Out-of-fold probability and predicted remainder for every task.
    prob_correct, _ = _cv_classification(
        groups, "correct", GROUP_NUM, CAT_COLS,
        lambda: RandomForestClassifier(
            n_estimators=300, min_samples_leaf=3, random_state=0, n_jobs=1
        ),
    )
    pred_remaining, _ = _cv_regression(
        groups, "remaining_cost", GROUP_NUM, CAT_COLS,
        lambda: HistGradientBoostingRegressor(
            max_iter=200, learning_rate=0.05, random_state=0
        ),
    )
    # On answered tasks the remainder is zero by construction; keep that.
    pred_remaining = np.where(groups["answered"] == 1, 0.0, np.maximum(0.0, pred_remaining))
    lambdas = [0.0, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]
    policy = groups[[
        "task_id", "rel", "task_type", "source", "reward", "cost",
        "total_cost", "remaining_cost", "answered", "correct",
        "impossible_label",
    ]].copy()
    policy["prob_correct"] = prob_correct
    policy["pred_remaining"] = pred_remaining
    policy.to_csv(args.out_dir / "policy_tasks.csv", index=False)
    selection = _selection_simulation(groups, prob_correct, pred_remaining, lambdas)
    for row in selection:
        print(row)
    report["selection"] = selection
    # Baselines: always run wave 2 on unanswered, never run it.
    always = _selection_simulation(groups, np.ones(len(groups)), pred_remaining, [0.0])
    never = _selection_simulation(groups, np.zeros(len(groups)), pred_remaining, [0.0])
    report["selection_baselines"] = {"always": always[0], "never": never[0]}
    print("always", always[0])
    print("never", never[0])

    (args.out_dir / "online_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nwrote {args.out_dir / 'online_report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
