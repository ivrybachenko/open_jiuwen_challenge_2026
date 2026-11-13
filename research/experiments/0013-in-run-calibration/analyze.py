#!/usr/bin/env python3
"""Check whether in-run calibration / fine-tuning can improve the result.

Three questions:

1. Does the harness observe the real label ("answer accepted") during a run?
   This is answered by inspecting the code and the regulation.
2. Do cheap proxy labels (answer present, exit code, tests seen) identify
   correctness well enough to be used as labels?
3. Does a monotone calibration transform change the wave-2 selection?  Does
   retraining on the current run's true labels (an oracle upper bound) improve
   the score?

Outputs ``results/report.json`` and a short ``results/summary.md``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "results"
RESULTS_0007 = (
    ROOT / "research" / "experiments"
    / "0007-predict-remaining-cost-during-solve" / "results"
)
MODEL_META = (
    ROOT / "harness" / "src" / "harness" / "application" / "models"
    / "online_model.json"
)

NUMERIC = json.loads(MODEL_META.read_text(encoding="utf-8"))["numeric_features"]
CATEGORICAL = json.loads(MODEL_META.read_text(encoding="utf-8"))[
    "categorical_features"
]


def _auc(y: np.ndarray, p: np.ndarray) -> float | None:
    y = np.asarray(y).astype(int)
    if len(np.unique(y)) < 2:
        return None
    return float(roc_auc_score(y, p))


def _brier(y: np.ndarray, p: np.ndarray) -> float:
    return float(brier_score_loss(np.asarray(y).astype(int), np.clip(p, 0, 1)))


def code_audit() -> dict[str, Any]:
    """Facts that decide whether real labels exist inside a run."""
    return {
        "harness_solved_field": (
            "harness/src/harness/application/solver.py: "
            "usable = answer is not None and answer_kind in {done, value}; "
            "this is what solutions.json calls solved"
        ),
        "evaluator_runs_after_harness": (
            "evaluation/harness_task_set_checker/checker.py runs "
            "evaluate_suite after run_harness returns; the harness never calls "
            "evaluation.answer_evaluator"
        ),
        "evaluator_does_not_trust_solved": (
            "evaluation/answer_evaluator/evaluator.py docstring: solved in "
            "solutions.json only means an answer was submitted"
        ),
        "regulation_no_feedback": (
            "challenge_info/problem_statement.md: final set is hidden until the "
            "run, the run is one pass within one hour, and hidden tests grade "
            "the submitted answer.txt after the run"
        ),
        "regulation_local_neural_models_forbidden": (
            "challenge_info/problem_statement.md: local neural models are "
            "forbidden; only four proxy models may be called; classical "
            "regression/boosting are allowed"
        ),
        "conclusion": (
            "During a run there is no ground-truth correctness label.  Only "
            "answer-present and execution signals are available.  Retraining a "
            "classical model is allowed, but it needs labels; fine-tuning an "
            "LLM is forbidden."
        ),
    }


def proxy_labels(frame: pd.DataFrame) -> dict[str, Any]:
    """AUC of cheap in-run signals against the evaluator verdict."""
    target = frame["correct"].astype(int).to_numpy()
    proxies = {
        "answer_present(answered)": frame["answered"].to_numpy(),
        "exit_code_zero": (frame["exit_code"].fillna(0) == 0).to_numpy(),
        "script_has_tests": frame["script_has_tests"].to_numpy(),
        "tests_in_overview": frame["tests_in_overview"].to_numpy(),
        "script_has_write_answer": frame["script_has_write_answer"].to_numpy(),
        "output_present": (frame["output_chars"] > 0).to_numpy(),
        "answer_kind_done": (frame["answer_kind"] == "done").to_numpy(),
        "answer_kind_value": (frame["answer_kind"] == "value").to_numpy(),
    }
    result: dict[str, Any] = {
        "n": int(len(frame)),
        "base_rate": float(target.mean()),
        "proxies": {},
    }
    for name, values in proxies.items():
        values = np.asarray(values).astype(float)
        auc = _auc(target, values)
        result["proxies"][name] = {
            "auc": auc,
            "brier": _brier(target, values),
            "positive_rate": float(values.mean()),
        }
    # Among answered tasks only: does "answer present" separate correct from
    # incorrect answers?  This is the ceiling for self-labelling.
    answered = frame[frame["answered"] == 1]
    result["among_answered"] = {
        "n": int(len(answered)),
        "base_rate": float(answered["correct"].mean()),
        "auc_answer_kind_done": _auc(
            answered["correct"].to_numpy(),
            (answered["answer_kind"] == "done").to_numpy(),
        ),
        "auc_script_has_tests": _auc(
            answered["correct"].to_numpy(),
            answered["script_has_tests"].to_numpy(),
        ),
        "auc_exit_code_zero": _auc(
            answered["correct"].to_numpy(),
            (answered["exit_code"].fillna(0) == 0).to_numpy(),
        ),
    }
    return result


def _selection_order(
    frame: pd.DataFrame, probability: np.ndarray
) -> np.ndarray:
    """Rank exactly like ``select_followups``: score, reward, task id."""
    expected_gain = frame["reward"].to_numpy() * np.asarray(probability)
    cost = frame["remaining_cost"].clip(lower=1.0).to_numpy()
    score = expected_gain / cost
    order = pd.DataFrame(
        {
            "score": score,
            "reward": frame["reward"].to_numpy(),
            "task_id": frame["task_id"].astype(str).to_numpy(),
        }
    ).sort_values(
        ["score", "reward", "task_id"],
        ascending=[False, False, True],
        kind="mergesort",
    )
    return order.index.to_numpy()


def _simulate(
    frame: pd.DataFrame,
    order: np.ndarray,
    budget: float,
) -> dict[str, float]:
    spent = 0.0
    score = 0.0
    runs = 0
    for index in order:
        row = frame.iloc[index]
        cost = float(row["remaining_cost"])
        if cost <= 0 or spent + cost > budget:
            continue
        spent += cost
        score += float(row["reward"]) * float(row["correct"])
        runs += 1
    return {
        "runs": runs,
        "score": score,
        "cost": spent,
        "score_per_1k": 1000.0 * score / max(1.0, spent),
    }


def _simulate_arrays(
    probability: np.ndarray,
    gains: np.ndarray,
    costs: np.ndarray,
    candidate: np.ndarray,
    budget: float,
) -> dict[str, float]:
    """Score a budgeted selection given arrays, using actual logged gains."""
    order = np.argsort(-(gains * probability / np.clip(costs, 1.0, None)))
    spent = 0.0
    score = 0.0
    runs = 0
    for index in order:
        if not candidate[index]:
            continue
        cost = float(costs[index])
        if cost <= 0 or spent + cost > budget:
            continue
        spent += cost
        score += float(gains[index])
        runs += 1
    return {
        "runs": runs,
        "score": score,
        "cost": spent,
        "score_per_1k": 1000.0 * score / max(1.0, spent),
    }


def calibration_invariance(frame: pd.DataFrame) -> dict[str, Any]:
    """Monotone transforms preserve the order and therefore the score."""
    p = frame["prob_correct"].clip(0.001, 0.999).to_numpy()
    # Strictly monotone transforms that a calibration step could apply.
    logit = np.log(p / (1.0 - p))
    transforms = {
        "identity": p,
        "logit_shift_+1": 1.0 / (1.0 + np.exp(-(logit + 1.0))),
        "platt_like": 1.0 / (1.0 + np.exp(-(3.0 * (p - 0.5)))),
        "power_2": p**2,
        "sqrt": np.sqrt(p),
    }
    total = float(frame["remaining_cost"].sum())
    output: dict[str, Any] = {"total_actual_remaining": total, "budgets": {}}
    for fraction in (0.1, 0.25, 0.5):
        budget = total * fraction
        output["budgets"][f"{fraction:.2f}"] = {}
        for name, transformed in transforms.items():
            order = _selection_order(frame, transformed)
            result = _simulate(frame, order, budget)
            output["budgets"][f"{fraction:.2f}"][name] = {
                **result,
                "order": order.tolist(),
            }
    # Compare orders: 1.0 means identical.
    base = np.asarray(output["budgets"]["0.25"]["identity"]["order"])
    output["order_agreement"] = {}
    for name, transformed in transforms.items():
        other = np.asarray(output["budgets"]["0.25"][name]["order"])
        output["order_agreement"][name] = float(np.mean(base == other))
    return output


def oracle_retraining(
    features: pd.DataFrame,
    labels: np.ndarray,
    groups: np.ndarray,
    n_splits: int = 20,
    run_size: int = 100,
) -> dict[str, Any]:
    """Upper bound: fit on the run's own labelled rows, then select wave 2.

    This is deliberately optimistic: the run is 100 tasks, the labels are
    revealed immediately, and the model is fitted in-sample.  If even this
    does not beat the static model, the hypothesis is dead.
    """
    rng = np.random.default_rng(20261113)
    unique_groups = np.unique(groups)
    results: list[dict[str, float]] = []
    for _ in range(n_splits):
        run_groups = rng.choice(
            unique_groups, size=min(run_size, len(unique_groups)), replace=False
        )
        mask = np.isin(groups, run_groups)
        x = features.loc[mask].to_numpy()
        y = labels[mask].astype(int)
        if len(np.unique(y)) < 2:
            continue
        model = Pipeline(
            [
                ("scale", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        max_iter=2000, C=0.1, class_weight="balanced"
                    ),
                ),
            ]
        )
        model.fit(x, y)
        probability = model.predict_proba(x)[:, 1]
        # The static comparator: the OOF probability shipped in 0007.
        static = features_static.loc[mask, "prob_correct"].to_numpy()
        gains = (
            features_static.loc[mask, "reward"].to_numpy()
            * features_static.loc[mask, "correct"].to_numpy()
        )
        costs = features_static.loc[mask, "remaining_cost"].clip(
            lower=0.0
        ).to_numpy()
        candidate = (
            features_static.loc[mask, "answered"].to_numpy() == 0
        )
        total = float(costs[candidate].sum())
        row: dict[str, Any] = {
            "auc_retrained": _auc(y, probability) or 0.0,
            "auc_static": _auc(y, static) or 0.0,
            "brier_retrained": _brier(y, probability),
            "brier_static": _brier(y, static),
        }
        for fraction in (0.1, 0.25, 0.5):
            budget = total * fraction
            for name, prob in (
                ("retrained", probability),
                ("static", static),
            ):
                row[f"score_{name}_{fraction:.2f}"] = _simulate_arrays(
                    prob, gains, costs, candidate, budget
                )
        results.append(row)
    summary: dict[str, Any] = {
        "n_splits": len(results),
        "auc_retrained_mean": float(np.mean([r["auc_retrained"] for r in results])),
        "auc_static_mean": float(np.mean([r["auc_static"] for r in results])),
        "brier_retrained_mean": float(
            np.mean([r["brier_retrained"] for r in results])
        ),
        "brier_static_mean": float(np.mean([r["brier_static"] for r in results])),
        "note": (
            "In-sample fit on 100 labelled tasks is an upper bound; a real run "
            "has no labels at all."
        ),
    }
    for fraction in (0.1, 0.25, 0.5):
        for name in ("retrained", "static"):
            key = f"score_{name}_{fraction:.2f}"
            summary[key] = {
                "mean_score_per_1k": float(
                    np.mean([r[key]["score_per_1k"] for r in results])
                ),
                "mean_score": float(np.mean([r[key]["score"] for r in results])),
                "mean_runs": float(np.mean([r[key]["runs"] for r in results])),
            }
    return summary


def _feature_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    x = frame[NUMERIC + CATEGORICAL].copy()
    for column in NUMERIC:
        x[column] = pd.to_numeric(x[column], errors="coerce").fillna(0.0)
    return pd.get_dummies(x, columns=CATEGORICAL, dummy_na=False)


def domain_shift(turns: pd.DataFrame, n_splits: int = 20, run_size: int = 100) -> dict[str, Any]:
    """Train on the 32-task research set, then adapt to a 100-task run.

    The hidden set is a new distribution, just as the research set is a
    different distribution from the fresh 240 tasks.  ``transfer`` is the
    static model; ``adapted`` is refitted on the run's own labels (oracle).
    """
    research = turns[turns["source"].astype(str).str.startswith("exp:")].copy()
    fresh = turns[turns["source"].astype(str).str.startswith("fresh:")].copy()
    # One row per run/task: the shipped model is a wave-1 model.
    research = research.drop_duplicates(["run_id", "task_id"])
    fresh = fresh.drop_duplicates(["task_id"]).merge(
        pd.read_csv(RESULTS_0007 / "online_fresh_predictions.csv")[
            ["task_id", "prob_correct"]
        ],
        on="task_id",
        how="left",
    )
    x_research = _feature_matrix(research)
    x_fresh = _feature_matrix(fresh)
    columns = sorted(set(x_research.columns) | set(x_fresh.columns))
    x_research = x_research.reindex(columns=columns, fill_value=0)
    x_fresh = x_fresh.reindex(columns=columns, fill_value=0)
    y_research = research["correct"].astype(int).to_numpy()
    y_fresh = fresh["correct"].astype(int).to_numpy()

    transfer_model = Pipeline(
        [
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(max_iter=3000, C=0.1,
                                       class_weight="balanced")),
        ]
    )
    transfer_model.fit(x_research.to_numpy(), y_research)
    transfer_p = transfer_model.predict_proba(x_fresh.to_numpy())[:, 1]
    static_p = fresh["prob_correct"].to_numpy()

    rng = np.random.default_rng(20261113)
    task_ids = fresh["task_id"].to_numpy()
    results: list[dict[str, float]] = []
    for _ in range(n_splits):
        run_ids = rng.choice(task_ids, size=min(run_size, len(task_ids)),
                             replace=False)
        mask = np.isin(task_ids, run_ids)
        x = x_fresh.loc[mask].to_numpy()
        y = y_fresh[mask]
        if len(np.unique(y)) < 2:
            continue
        model = Pipeline(
            [
                ("scale", StandardScaler()),
                ("clf", LogisticRegression(max_iter=3000, C=0.1,
                                           class_weight="balanced")),
            ]
        )
        model.fit(x, y)
        adapted_p = model.predict_proba(x)[:, 1]
        run = fresh.loc[mask].reset_index(drop=True)
        gains = run["reward"].to_numpy() * y
        costs = run["remaining_cost"].clip(lower=0.0).to_numpy()
        candidate = run["answered"].to_numpy() == 0
        total = float(costs[candidate].sum())
        row: dict[str, Any] = {
            "auc_transfer": _auc(y, transfer_p[mask]) or 0.0,
            "auc_adapted": _auc(y, adapted_p) or 0.0,
            "auc_static": _auc(y, static_p[mask]) or 0.0,
            "brier_transfer": _brier(y, transfer_p[mask]),
            "brier_adapted": _brier(y, adapted_p),
        }
        for fraction in (0.1, 0.25, 0.5):
            budget = total * fraction
            for name, prob in (
                ("transfer", transfer_p[mask]),
                ("adapted", adapted_p),
                ("static", static_p[mask]),
            ):
                row[f"score_{name}_{fraction:.2f}"] = _simulate_arrays(
                    prob, gains, costs, candidate, budget
                )
        results.append(row)

    summary: dict[str, Any] = {
        "n_splits": len(results),
        "auc_transfer_mean": float(np.mean([r["auc_transfer"] for r in results])),
        "auc_adapted_mean": float(np.mean([r["auc_adapted"] for r in results])),
        "auc_static_mean": float(np.mean([r["auc_static"] for r in results])),
        "brier_transfer_mean": float(
            np.mean([r["brier_transfer"] for r in results])
        ),
        "brier_adapted_mean": float(
            np.mean([r["brier_adapted"] for r in results])
        ),
        "note": (
            "transfer = trained on the 32-task research set; static = shipped "
            "OOF model; adapted = refitted in-sample on the 100-task run's "
            "true labels (oracle, unavailable in a real run)."
        ),
    }
    for fraction in (0.1, 0.25, 0.5):
        for name in ("transfer", "adapted", "static"):
            key = f"score_{name}_{fraction:.2f}"
            summary[key] = {
                "mean_score_per_1k": float(
                    np.mean([r[key]["score_per_1k"] for r in results])
                ),
                "mean_score": float(np.mean([r[key]["score"] for r in results])),
            }
    return summary


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    policy = pd.read_csv(RESULTS_0007 / "policy_tasks.csv")
    fresh = pd.read_csv(RESULTS_0007 / "online_fresh_predictions.csv")
    turns = pd.read_csv(RESULTS_0007 / "turn_groups.csv")

    candidates = policy[policy["answered"] == 0].reset_index(drop=True).copy()
    candidates["remaining_cost"] = candidates["remaining_cost"].clip(lower=0)

    report: dict[str, Any] = {
        "code_audit": code_audit(),
        "proxy_labels_all": proxy_labels(turns),
        "proxy_labels_fresh": proxy_labels(
            turns[turns["source"].astype(str).str.startswith("fresh:")]
        ),
        "calibration_invariance": calibration_invariance(candidates),
        "domain_shift": domain_shift(turns),
    }

    # Oracle retraining needs features and the static OOF probability on the
    # same rows.  Build one row per fresh task.
    global features_static
    features_static = turns[
        turns["source"].astype(str).str.startswith("fresh:")
    ].copy()
    features_static = features_static.merge(
        fresh[["task_id", "prob_correct"]], on="task_id", how="left"
    )
    features_static = features_static.dropna(subset=["prob_correct"])
    feature_columns = NUMERIC + CATEGORICAL
    x = features_static[feature_columns].copy()
    for column in NUMERIC:
        x[column] = pd.to_numeric(x[column], errors="coerce").fillna(0.0)
    x = pd.get_dummies(x, columns=CATEGORICAL, dummy_na=False)
    labels = features_static["correct"].astype(int).to_numpy()
    groups = features_static["task_id"].to_numpy()
    report["oracle_retraining"] = oracle_retraining(x, labels, groups)

    # Static baseline on the same rows.
    static = features_static["prob_correct"].to_numpy()
    report["static_fresh"] = {
        "n": int(len(features_static)),
        "auc": _auc(labels, static),
        "brier": _brier(labels, static),
        "base_rate": float(labels.mean()),
    }

    (OUT / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2)[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
