#!/usr/bin/env python3
"""Compare one wave-1 model with separate models for each later wave.

The decision after wave ``w`` is: spend one more turn on a candidate task, or
stop.  The target is the final evaluator verdict.  Rows are grouped by task so
repeated runs of the same task never leak between train and test.

Outputs ``results/report.json`` and ``results/summary.md``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
TURNS = OUT / "turns.csv"
MODEL_META = (
    ROOT / "harness" / "src" / "harness" / "application" / "models"
    / "online_model.json"
)
META = json.loads(MODEL_META.read_text(encoding="utf-8"))
NUMERIC = META["numeric_features"]
CATEGORICAL = META["categorical_features"]
NOREASON = "qwen3.6-35b-a3b-noreason"


def _auc(y: np.ndarray, p: np.ndarray) -> float | None:
    y = np.asarray(y).astype(int)
    if len(np.unique(y)) < 2:
        return None
    return float(roc_auc_score(y, p))


def _pr_auc(y: np.ndarray, p: np.ndarray) -> float | None:
    y = np.asarray(y).astype(int)
    if len(np.unique(y)) < 2:
        return None
    return float(average_precision_score(y, p))


def _brier(y: np.ndarray, p: np.ndarray) -> float:
    return float(brier_score_loss(np.asarray(y).astype(int), np.clip(p, 0, 1)))


def _ece(y: np.ndarray, p: np.ndarray, bins: int = 5) -> float:
    y = np.asarray(y).astype(int)
    p = np.clip(np.asarray(p), 0, 1)
    edges = np.linspace(0.0, 1.0, bins + 1)
    total = 0.0
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (p >= low) & (p < high if high < 1.0 else p <= high)
        if not mask.any():
            continue
        total += mask.mean() * abs(float(y[mask].mean()) - float(p[mask].mean()))
    return float(total)


def _evaluate(y: np.ndarray, p: np.ndarray) -> dict[str, Any]:
    return {
        "n": int(len(y)),
        "positive": int(np.sum(y)),
        "base_rate": float(np.mean(y)) if len(y) else None,
        "auc": _auc(y, p),
        "pr_auc": _pr_auc(y, p),
        "brier": _brier(y, p),
        "ece": _ece(y, p),
        "mean_prediction": float(np.mean(p)) if len(p) else None,
    }


def _bootstrap_auc(
    y: np.ndarray, p: np.ndarray, groups: np.ndarray, rounds: int = 300
) -> list[float]:
    rng = np.random.default_rng(20261113)
    unique = np.unique(groups)
    values: list[float] = []
    for _ in range(rounds):
        sample = rng.choice(unique, size=len(unique), replace=True)
        mask = np.isin(groups, sample)
        auc = _auc(y[mask], p[mask])
        if auc is not None:
            values.append(auc)
    if not values:
        return [float("nan"), float("nan")]
    return [float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))]


def _make_model(kind: str, columns: list[str]) -> Pipeline:
    numeric = [c for c in columns if c in NUMERIC or c in {"wave", "turn"}]
    categorical = [c for c in columns if c in CATEGORICAL]
    transformers = [
        (
            "num",
            Pipeline(
                [
                    ("impute", SimpleImputer(strategy="constant", fill_value=0)),
                    ("scale", StandardScaler()),
                ]
            ),
            numeric,
        ),
        (
            "cat",
            Pipeline(
                [
                    (
                        "impute",
                        SimpleImputer(strategy="constant", fill_value="none"),
                    ),
                    (
                        "onehot",
                        OneHotEncoder(handle_unknown="ignore"),
                    ),
                ]
            ),
            categorical,
        ),
    ]
    pre = ColumnTransformer(transformers)
    if kind == "logreg":
        clf = LogisticRegression(
            max_iter=4000, C=0.3, class_weight="balanced"
        )
    else:
        clf = RandomForestClassifier(
            n_estimators=400,
            min_samples_leaf=3,
            class_weight="balanced_subsample",
            random_state=20261113,
            n_jobs=1,
        )
    return Pipeline([("pre", pre), ("clf", clf)])


def _oof_predictions(
    frame: pd.DataFrame,
    *,
    target_wave: int,
    train_wave: int,
    columns: list[str],
    kind: str,
    n_splits: int = 5,
) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    """Out-of-fold predictions on the target wave, grouped by task."""
    test = frame[frame["wave"] == target_wave].reset_index(drop=True)
    if len(test) < 6 or test["final_correct"].nunique() < 2:
        return None
    groups = test["task_id"].to_numpy()
    n_groups = len(np.unique(groups))
    if n_groups < 4:
        return None
    splits = min(n_splits, n_groups)
    predictions = np.full(len(test), np.nan)
    for train_index, test_index in GroupKFold(n_splits=splits).split(
        test, groups=groups
    ):
        train_tasks = set(test.iloc[train_index]["task_id"])
        train = frame[
            (frame["wave"] == train_wave)
            & (frame["task_id"].isin(train_tasks))
        ].reset_index(drop=True)
        if len(train) < 8 or train["final_correct"].nunique() < 2:
            continue
        model = _make_model(kind, columns)
        model.fit(train[columns], train["final_correct"].astype(int))
        predictions[test_index] = model.predict_proba(test.iloc[test_index][columns])[
            :, 1
        ]
    mask = ~np.isnan(predictions)
    if mask.sum() < 6:
        return None
    return (
        test.loc[mask, "final_correct"].astype(int).to_numpy(),
        predictions[mask],
        test.loc[mask, "task_id"].to_numpy(),
        test.loc[mask].reset_index(drop=True),
    )


def _utility(
    frame: pd.DataFrame,
    probability: np.ndarray,
    *,
    fraction: float = 0.5,
) -> dict[str, float]:
    """Actual gain per 1k tokens when the top ``fraction`` is selected."""
    gains = (
        frame["reward"].to_numpy()
        * frame["final_correct"].astype(int).to_numpy()
    )
    costs = frame["next_cost"].clip(lower=1.0).to_numpy()
    expected = gains * np.asarray(probability)
    order = np.argsort(-(expected / costs))
    k = max(1, int(len(frame) * fraction))
    selected = order[:k]
    oracle_order = np.argsort(-(gains / costs))
    oracle = oracle_order[:k]
    return {
        "top_fraction": fraction,
        "policy_score_per_1k": float(
            1000.0 * gains[selected].sum() / max(1.0, costs[selected].sum())
        ),
        "oracle_score_per_1k": float(
            1000.0 * gains[oracle].sum() / max(1.0, costs[oracle].sum())
        ),
        "all_score_per_1k": float(
            1000.0 * gains.sum() / max(1.0, costs.sum())
        ),
    }


def _shipped_predictions(frame: pd.DataFrame) -> np.ndarray | None:
    """Apply the model shipped in the harness to arbitrary candidate rows."""
    model_path = (
        ROOT / "harness" / "src" / "harness" / "application" / "models"
        / "online_correct_model.joblib"
    )
    try:
        import joblib

        model = joblib.load(model_path)
    except Exception:  # noqa: BLE001 - optional baseline
        return None
    columns = NUMERIC + CATEGORICAL
    row = frame[columns].copy()
    for column in NUMERIC:
        row[column] = pd.to_numeric(row[column], errors="coerce").fillna(0.0)
    for column in CATEGORICAL:
        row[column] = row[column].fillna("none").astype(str)
    try:
        return model.predict_proba(row)[:, 1]
    except Exception:  # noqa: BLE001
        return None


def _oof_pooled(
    frame: pd.DataFrame,
    *,
    target_wave: int,
    columns: list[str],
    kind: str,
    n_splits: int = 5,
) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    """Train on all earlier waves of the training tasks, test on the target."""
    test = frame[frame["wave"] == target_wave].reset_index(drop=True)
    if len(test) < 6 or test["final_correct"].nunique() < 2:
        return None
    groups = test["task_id"].to_numpy()
    if len(np.unique(groups)) < 4:
        return None
    predictions = np.full(len(test), np.nan)
    for train_index, test_index in GroupKFold(
        n_splits=min(n_splits, len(np.unique(groups)))
    ).split(test, groups=groups):
        train_tasks = set(test.iloc[train_index]["task_id"])
        train = frame[
            (frame["task_id"].isin(train_tasks))
            & (frame["wave"] < target_wave)
        ].reset_index(drop=True)
        if target_wave == 1:
            train = frame[
                (frame["task_id"].isin(train_tasks)) & (frame["wave"] == 1)
            ].reset_index(drop=True)
        if len(train) < 8 or train["final_correct"].nunique() < 2:
            continue
        model = _make_model(kind, columns)
        model.fit(train[columns], train["final_correct"].astype(int))
        predictions[test_index] = model.predict_proba(
            test.iloc[test_index][columns]
        )[:, 1]
    mask = ~np.isnan(predictions)
    if mask.sum() < 6:
        return None
    return (
        test.loc[mask, "final_correct"].astype(int).to_numpy(),
        predictions[mask],
        test.loc[mask, "task_id"].to_numpy(),
        test.loc[mask].reset_index(drop=True),
    )


def _platt_oof(
    frame: pd.DataFrame,
    *,
    target_wave: int,
    n_splits: int = 5,
) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    """Wave-specific Platt calibration of the shipped model, out of fold."""
    test = frame[frame["wave"] == target_wave].reset_index(drop=True)
    if "shipped_p" not in test or len(test) < 6:
        return None
    if test["final_correct"].nunique() < 2:
        return None
    groups = test["task_id"].to_numpy()
    if len(np.unique(groups)) < 4:
        return None
    predictions = np.full(len(test), np.nan)
    for train_index, test_index in GroupKFold(
        n_splits=min(n_splits, len(np.unique(groups)))
    ).split(test, groups=groups):
        train_tasks = set(test.iloc[train_index]["task_id"])
        train = frame[
            (frame["wave"] == target_wave)
            & (frame["task_id"].isin(train_tasks))
        ]
        if len(train) < 8 or train["final_correct"].nunique() < 2:
            continue
        p_train = np.clip(train["shipped_p"].to_numpy(), 0.001, 0.999)
        logit_train = np.log(p_train / (1.0 - p_train)).reshape(-1, 1)
        calibrator = LogisticRegression(max_iter=1000)
        calibrator.fit(logit_train, train["final_correct"].astype(int))
        p_test = np.clip(
            test.iloc[test_index]["shipped_p"].to_numpy(), 0.001, 0.999
        )
        logit_test = np.log(p_test / (1.0 - p_test)).reshape(-1, 1)
        predictions[test_index] = calibrator.predict_proba(logit_test)[:, 1]
    mask = ~np.isnan(predictions)
    if mask.sum() < 6:
        return None
    return (
        test.loc[mask, "final_correct"].astype(int).to_numpy(),
        predictions[mask],
        test.loc[mask, "task_id"].to_numpy(),
        test.loc[mask].reset_index(drop=True),
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(TURNS)
    frame = frame[frame["model"] == NOREASON].copy()
    frame = frame[frame["final_correct"].notna()].copy()
    frame["final_correct"] = frame["final_correct"].astype(bool)

    # The last wave of a run is not a real "continue" decision.
    run_max = frame.groupby("run_id")["n_waves"].transform("max")
    frame["run_max_waves"] = run_max

    candidates = frame[
        frame["answer_kind"].isin(["none", "impossible"])
    ].copy()
    candidates = candidates[candidates["wave"] < candidates["run_max_waves"]]
    candidates["shipped_p"] = _shipped_predictions(candidates)

    report: dict[str, Any] = {
        "data": {
            "turns": int(len(frame)),
            "candidate_decision_rows": int(len(candidates)),
            "tasks": int(candidates["task_id"].nunique()),
            "runs": int(candidates["run_id"].nunique()),
            "by_wave": {
                str(wave): {
                    "rows": int(len(group)),
                    "tasks": int(group["task_id"].nunique()),
                    "base_rate": float(group["final_correct"].mean()),
                }
                for wave, group in candidates.groupby("wave")
            },
        },
        "comparisons": {},
    }

    base_columns = NUMERIC + CATEGORICAL
    plus_wave_columns = base_columns + ["wave", "turn"]

    for target_wave in sorted(candidates["wave"].unique()):
        if target_wave >= candidates["run_max_waves"].max():
            continue
        report["comparisons"][str(target_wave)] = {}
        target = candidates[candidates["wave"] == target_wave]
        shipped = _shipped_predictions(target)
        if shipped is not None and target["final_correct"].nunique() > 1:
            metrics = _evaluate(
                target["final_correct"].astype(int).to_numpy(), shipped
            )
            metrics["auc_ci95"] = _bootstrap_auc(
                target["final_correct"].astype(int).to_numpy(),
                shipped,
                target["task_id"].to_numpy(),
            )
            metrics["utility"] = _utility(target, shipped)
            report["comparisons"][str(target_wave)]["shipped_model"] = metrics
        platt = _platt_oof(candidates, target_wave=int(target_wave))
        if platt is not None:
            y, p, groups, subset = platt
            metrics = _evaluate(y, p)
            metrics["auc_ci95"] = _bootstrap_auc(y, p, groups)
            metrics["utility"] = _utility(subset, p)
            report["comparisons"][str(target_wave)]["shipped_platt"] = metrics

        for kind in ("logreg", "rf"):
            variants: dict[str, tuple[int, list[str]]] = {
                "wave1_model": (1, base_columns),
                "same_wave_model": (int(target_wave), base_columns),
            }
            if target_wave > 1:
                variants["previous_wave_model"] = (
                    int(target_wave) - 1,
                    base_columns,
                )
            for name, (train_wave, columns) in variants.items():
                result = _oof_predictions(
                    candidates,
                    target_wave=int(target_wave),
                    train_wave=train_wave,
                    columns=columns,
                    kind=kind,
                )
                if result is None:
                    continue
                y, p, groups, subset = result
                metrics = _evaluate(y, p)
                metrics["auc_ci95"] = _bootstrap_auc(y, p, groups)
                metrics["utility"] = _utility(subset, p)
                report["comparisons"][str(target_wave)][f"{kind}:{name}"] = metrics

            # Pooled model with the wave as a feature, trained on earlier
            # waves only (the realistic option when labels are available).
            result = _oof_pooled(
                candidates,
                target_wave=int(target_wave),
                columns=plus_wave_columns,
                kind=kind,
            )
            if result is not None:
                y, p, groups, subset = result
                metrics = _evaluate(y, p)
                metrics["auc_ci95"] = _bootstrap_auc(y, p, groups)
                metrics["utility"] = _utility(subset, p)
                report["comparisons"][str(target_wave)][f"{kind}:pooled_plus_wave"] = (
                    metrics
                )

    (OUT / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2)[:5000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
