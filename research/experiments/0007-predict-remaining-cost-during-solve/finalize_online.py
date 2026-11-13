#!/usr/bin/env python3
"""Finalize the online predictor bundle for experiment 0007.

Deployable pieces:

* ``online_correct_model.joblib`` -- P(correct after solving) from wave-1
  features, trained on the 240 fresh tasks;
* ``online_predictor.json`` -- feature list, metrics and the next-turn cost
  formula.

Usage::

    harness/.venv/bin/python \
        research/experiments/0007-predict-remaining-cost-during-solve/finalize_online.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score, brier_score_loss, roc_auc_score,
)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline

EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[2]
sys.path.insert(0, str(ROOT / "harness" / "src"))
from harness.application.features import promise_score  # noqa: E402,F401

from train_online import (  # noqa: E402
    CAT_COLS, GROUP_NUM, _ece, _preprocessor,
)


def main() -> int:
    import joblib

    groups = pd.read_csv(EXP / "results" / "turn_groups.csv")
    fresh = groups[groups["source"].str.startswith("fresh")].copy()
    fresh = fresh[fresh["has_correctness"] == 1]
    print("fresh groups", len(fresh), flush=True)
    X = fresh[GROUP_NUM + CAT_COLS]
    y = fresh["correct"].astype(int).values

    # Out-of-fold metrics on the fresh tasks.
    pred = np.zeros(len(fresh))
    for train_idx, test_idx in GroupKFold(n_splits=5).split(
            fresh, y, groups=fresh["task_id"]):
        pipe = Pipeline([
            ("pre", _preprocessor(GROUP_NUM, CAT_COLS)),
            ("model", RandomForestClassifier(
                n_estimators=300, min_samples_leaf=3, random_state=0,
                n_jobs=1)),
        ])
        pipe.fit(X.iloc[train_idx], y[train_idx])
        pred[test_idx] = pipe.predict_proba(X.iloc[test_idx])[:, 1]
    metrics = {
        "n": int(len(fresh)),
        "tasks": int(fresh["task_id"].nunique()),
        "auc": float(roc_auc_score(y, pred)),
        "pr_auc": float(average_precision_score(y, pred)),
        "brier": float(brier_score_loss(y, pred)),
        "ece": float(_ece(y, pred)),
        "base_rate": float(y.mean()),
        "mean_prediction": float(pred.mean()),
    }
    print(metrics, flush=True)

    fresh_out = fresh[[
        "task_id", "rel", "task_type", "source", "reward", "cost",
        "total_cost", "remaining_cost", "answered", "correct",
        "impossible_label",
    ]].copy()
    fresh_out["prob_correct"] = pred
    fresh_out["pred_remaining"] = 230.0
    fresh_out.to_csv(EXP / "results" / "online_fresh_predictions.csv", index=False)

    model = Pipeline([
        ("pre", _preprocessor(GROUP_NUM, CAT_COLS)),
        ("model", RandomForestClassifier(
            n_estimators=400, min_samples_leaf=3, random_state=0, n_jobs=1)),
    ])
    model.fit(X, y)
    joblib.dump(model, EXP / "results" / "online_correct_model.joblib")

    pairs = pd.read_csv(EXP / "results" / "turn_pairs.csv")
    payload = {
        "target": "P(answer is correct after solving | wave-1 features)",
        "model": "RandomForestClassifier(n_estimators=400, min_samples_leaf=3)",
        "numeric_features": GROUP_NUM,
        "categorical_features": CAT_COLS,
        "oof_metrics_fresh": metrics,
        "trained_tasks": int(fresh["task_id"].nunique()),
        "next_turn_cost_formula": "prev_input + prev_output + exec_chars/4 + 154",
        "next_turn_formula_mae": float(np.mean(np.abs(
            pairs["next_input"]
            - (pairs["prev_input"] + pairs["prev_output"]
               + pairs["exec_chars"] / 4.0 + 154.0)))),
        "selection_rule": "run wave 2 if P(correct) * reward > lambda * expected_retry_cost",
        "caveat": "Trained on synthetic tasks; calibrate on real tasks.",
    }
    (EXP / "results" / "online_predictor.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote online_predictor.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
