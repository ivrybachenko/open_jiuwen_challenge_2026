#!/usr/bin/env python3
"""Train and ship the wave-specific success models.

The models are trained on the multi-wave dataset from experiment ``0012``:

* wave 2: rows after wave 1, labelled with the final evaluator verdict;
* wave 3: rows after wave 2 (more data than wave-3 rows, and the pilot showed
  it transfers better than a wave-3-only model);
* wave 4: rows after wave 3.

Wave 1 and waves without a model keep the global ``online_correct_model``.
The script writes ``wave_models.joblib`` and ``wave_model.json`` next to the
global model and a report in the experiment directory.

Usage::

    harness/.venv/bin/python \
      research/experiments/0012-wave-specific-models/train_wave_models.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MODEL_DIR = (
    ROOT / "harness" / "src" / "harness" / "solving" / "success_predictors"
    / "models"
)
META_PATH = MODEL_DIR / "online_model.json"
TURNS = HERE / "results" / "turns.csv"
REPORT = HERE / "results" / "wave_models_report.json"
NOREASON = "qwen3.6-35b-a3b-noreason"

META = json.loads(META_PATH.read_text(encoding="utf-8"))
NUMERIC = META["numeric_features"]
CATEGORICAL = META["categorical_features"]
COLUMNS = NUMERIC + CATEGORICAL


def _load_rows() -> pd.DataFrame:
    frame = pd.read_csv(TURNS)
    frame = frame[frame["model"] == NOREASON].copy()
    frame = frame[frame["final_correct"].notna()].copy()
    frame["final_correct"] = frame["final_correct"].astype(bool)
    run_max = frame.groupby("run_id")["n_waves"].transform("max")
    frame["run_max_waves"] = run_max
    frame = frame[frame["answer_kind"].isin(["none", "impossible"])].copy()
    frame = frame[frame["wave"] < frame["run_max_waves"]].copy()
    return frame


def _preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        [
            (
                "num",
                Pipeline(
                    [
                        (
                            "impute",
                            SimpleImputer(strategy="constant", fill_value=0),
                        ),
                        ("scale", StandardScaler()),
                    ]
                ),
                NUMERIC,
            ),
            (
                "cat",
                Pipeline(
                    [
                        (
                            "impute",
                            SimpleImputer(
                                strategy="constant", fill_value="none"
                            ),
                        ),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                CATEGORICAL,
            ),
        ]
    )


def _model(kind: str) -> Pipeline | VotingClassifier:
    if kind == "logreg":
        return Pipeline(
            [
                ("pre", _preprocessor()),
                (
                    "clf",
                    LogisticRegression(
                        max_iter=4000, C=0.3, class_weight="balanced"
                    ),
                ),
            ]
        )
    if kind == "rf":
        return Pipeline(
            [
                ("pre", _preprocessor()),
                (
                    "clf",
                    RandomForestClassifier(
                        n_estimators=400,
                        min_samples_leaf=3,
                        class_weight="balanced_subsample",
                        random_state=20261113,
                        n_jobs=1,
                    ),
                ),
            ]
        )
    if kind == "ensemble":
        return VotingClassifier(
            estimators=[
                ("logreg", _model("logreg")),
                ("rf", _model("rf")),
            ],
            voting="soft",
        )
    raise ValueError(f"unknown model kind: {kind}")


def _auc(y: np.ndarray, p: np.ndarray) -> float | None:
    y = np.asarray(y).astype(int)
    if len(np.unique(y)) < 2:
        return None
    return float(roc_auc_score(y, p))


def _brier(y: np.ndarray, p: np.ndarray) -> float:
    return float(brier_score_loss(np.asarray(y).astype(int), np.clip(p, 0, 1)))


def _ece(y: np.ndarray, p: np.ndarray, bins: int = 5) -> float:
    y = np.asarray(y).astype(int)
    p = np.clip(np.asarray(p), 0, 1)
    edges = np.linspace(0.0, 1.0, bins + 1)
    total = 0.0
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (p >= low) & (p < high if high < 1.0 else p <= high)
        if mask.any():
            total += mask.mean() * abs(float(y[mask].mean()) - float(p[mask].mean()))
    return float(total)


def _metrics(y: np.ndarray, p: np.ndarray) -> dict[str, Any]:
    return {
        "n": int(len(y)),
        "positive": int(np.sum(y)),
        "base_rate": float(np.mean(y)) if len(y) else None,
        "auc": _auc(y, p),
        "brier": _brier(y, p),
        "ece": _ece(y, p),
        "mean_prediction": float(np.mean(p)) if len(p) else None,
    }


def _oof(
    frame: pd.DataFrame,
    *,
    target_wave: int,
    train_wave: int,
    kind: str,
    n_splits: int = 5,
) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
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
            (frame["wave"] == train_wave)
            & (frame["task_id"].isin(train_tasks))
        ].reset_index(drop=True)
        if len(train) < 8 or train["final_correct"].nunique() < 2:
            continue
        model = _model(kind)
        model.fit(train[COLUMNS], train["final_correct"].astype(int))
        predictions[test_index] = model.predict_proba(
            test.iloc[test_index][COLUMNS]
        )[:, 1]
    mask = ~np.isnan(predictions)
    if mask.sum() < 6:
        return None
    return (
        test.loc[mask, "final_correct"].astype(int).to_numpy(),
        predictions[mask],
        test.loc[mask, "task_id"].to_numpy(),
    )


def _fit_final(frame: pd.DataFrame, *, train_wave: int, kind: str):
    train = frame[frame["wave"] == train_wave].reset_index(drop=True)
    if len(train) < 8 or train["final_correct"].nunique() < 2:
        raise ValueError(f"not enough rows for wave {train_wave}: {len(train)}")
    model = _model(kind)
    model.fit(train[COLUMNS], train["final_correct"].astype(int))
    return model, train


def main() -> int:
    frame = _load_rows()
    print(
        f"rows: {len(frame)}; waves: "
        + ", ".join(
            f"{int(wave)}={len(group)}"
            for wave, group in frame.groupby("wave")
        )
    )

    # Choice from the OOF report: RF for wave 2, the logreg+RF ensemble for
    # wave 3, logreg for wave 4.  The script still evaluates all three for the
    # report, so the choice is reproducible.
    plan = {
        2: {"train_wave": 2, "kind": "rf"},
        3: {"train_wave": 2, "kind": "ensemble"},
        4: {"train_wave": 4, "kind": "logreg"},
    }
    report: dict[str, Any] = {
        "target": "P(final answer accepted | features of the current turn)",
        "training_rows": int(len(frame)),
        "by_wave": {
            str(int(wave)): int(len(group))
            for wave, group in frame.groupby("wave")
        },
        "models": {},
        "oof": {},
        "caveat": (
            "Trained on synthetic tasks from experiment 0012; validate on a "
            "larger, more diverse set before trusting the absolute values."
        ),
    }

    models: dict[str, Any] = {}
    for target_wave, choice in plan.items():
        train_wave = int(choice["train_wave"])
        kind = str(choice["kind"])
        report["oof"][str(target_wave)] = {}
        for candidate in ("logreg", "rf", "ensemble"):
            result = _oof(
                frame,
                target_wave=target_wave,
                train_wave=train_wave,
                kind=candidate,
            )
            if result is None:
                continue
            y, p, groups = result
            report["oof"][str(target_wave)][candidate] = _metrics(y, p)
        model, train = _fit_final(frame, train_wave=train_wave, kind=kind)
        models[str(target_wave)] = model
        report["models"][str(target_wave)] = {
            "train_wave": train_wave,
            "kind": kind,
            "train_rows": int(len(train)),
            "train_tasks": int(train["task_id"].nunique()),
            "train_positive": int(train["final_correct"].sum()),
        }

    # Evaluate the wave-4 model on wave-5 rows as a possible fallback.
    wave4 = models.get("4")
    wave5 = frame[frame["wave"] == 5].reset_index(drop=True)
    if wave4 is not None and len(wave5) >= 6:
        p = wave4.predict_proba(wave5[COLUMNS])[:, 1]
        report["wave4_on_wave5"] = _metrics(
            wave5["final_correct"].astype(int).to_numpy(), p
        )
        report["wave4_on_wave5"]["note"] = (
            "Out-of-distribution check; only one positive in wave 5."
        )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(models, MODEL_DIR / "wave_models.joblib")
    wave_meta = {
        "target": report["target"],
        "models": {
            wave: {
                "train_wave": info["train_wave"],
                "kind": info["kind"],
                "train_rows": info["train_rows"],
                "train_tasks": info["train_tasks"],
            }
            for wave, info in report["models"].items()
        },
        "numeric_features": NUMERIC,
        "categorical_features": CATEGORICAL,
        "fallback": (
            "wave 1 and waves without a model use online_correct_model.joblib; "
            "if it is unavailable, the heuristic is used"
        ),
        "late_waves": (
            "wave 4 model for waves 5+; only 21 wave-5 rows (one positive), "
            "so this is a calibrated extrapolation, not a dedicated model"
        ),
        "oof": report["oof"],
        "caveat": report["caveat"],
    }
    (MODEL_DIR / "wave_model.json").write_text(
        json.dumps(wave_meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"models: {MODEL_DIR / 'wave_models.joblib'}")
    print(f"metadata: {MODEL_DIR / 'wave_model.json'}")
    print(f"report: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
