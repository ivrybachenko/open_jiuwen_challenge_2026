#!/usr/bin/env python3
"""Do text features add anything to structural features?

The competition allows classical models but not local neural networks, so an
"embedding" here means TF-IDF over the instruction (word and character
n-grams).  We compare:

* structural features only;
* TF-IDF only;
* structural + TF-IDF.

Targets are pre-solve cost and the synthetic impossible/solvable label.  The
important splits are leave-one-category-out and leave-one-generation-block-out.

Usage::

    harness/.venv/bin/python \
        research/experiments/0008-text-vs-structural-features/run_text_model.py
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import warnings
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    average_precision_score,
    mean_absolute_error,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[3]
EXP6 = ROOT / "research" / "experiments" / "0006-predict-cost-before-solve"
sys.path.insert(0, str(EXP6))
sys.path.insert(0, str(ROOT / "harness" / "src"))

from static_features import _strip_boilerplate  # noqa: E402
from train_static import (  # noqa: E402
    EXCLUDE, _block, _load_targets, _spearman,
)

warnings.filterwarnings("ignore")


def _load(tasks_dir: Path) -> pd.DataFrame:
    rows = []
    for tj in sorted(tasks_dir.glob("*/[!.]*/[!.]*/task.json")):
        meta = json.loads(tj.read_text(encoding="utf-8"))
        rows.append({
            "rel": "/".join(tj.parts[-4:-1]),
            "task_id": meta.get("task_id", ""),
            "task_type": meta.get("task_type", tj.parts[-4]),
            "label": tj.parts[-3],
            "instruction": _strip_boilerplate(meta.get("instruction", "")),
        })
    return pd.DataFrame(rows)


def _numeric_columns(df: pd.DataFrame) -> list[str]:
    drop = set(EXCLUDE) | {"instruction"}
    return [c for c in df.columns
            if c not in drop and pd.api.types.is_numeric_dtype(df[c])]


def _pre(num: list[str], cat: list[str], text_mode: str | None) -> ColumnTransformer:
    transformers: list[Any] = []
    if text_mode == "word":
        transformers.append(("text", TfidfVectorizer(
            lowercase=True, ngram_range=(1, 2), min_df=2, max_features=4000,
            sublinear_tf=True, stop_words="english",
        ), "instruction"))
    elif text_mode == "char":
        transformers.append(("text", TfidfVectorizer(
            lowercase=True, analyzer="char_wb", ngram_range=(3, 5),
            min_df=2, max_features=8000, sublinear_tf=True,
        ), "instruction"))
    if num:
        transformers.append(("num", Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]), num))
    if cat:
        transformers.append(("cat", OneHotEncoder(
            handle_unknown="ignore", sparse_output=False), cat))
    return ColumnTransformer(transformers)


def _split(mode: str, df: pd.DataFrame):
    if mode == "category":
        return LeaveOneGroupOut(), df["task_type"]
    if mode == "block":
        return LeaveOneGroupOut(), df["block"]
    return GroupKFold(n_splits=5), df["task_id"]


def _regression(
    df: pd.DataFrame, target: str, num: list[str], cat: list[str],
    text_mode: str | None, mode: str,
) -> dict[str, float]:
    data = df.dropna(subset=[target]).copy()
    y = data[target].astype(float).values
    pred = np.zeros(len(data))
    splitter, groups = _split(mode, data)
    for train_idx, test_idx in splitter.split(data, y, groups=groups):
        model = Ridge(alpha=10.0)
        pipe = Pipeline([("pre", _pre(num, cat, text_mode)), ("model", model)])
        pipe.fit(data.iloc[train_idx], np.log1p(y[train_idx]))
        fold = np.expm1(pipe.predict(data.iloc[test_idx]))
        low, high = np.percentile(y[train_idx], [1, 99])
        pred[test_idx] = np.clip(fold, max(1.0, low), high)
    return {
        "mae": float(mean_absolute_error(y, pred)),
        "r2": float(r2_score(y, pred)),
        "spearman": _spearman(y, pred),
    }


def _classification(
    df: pd.DataFrame, target: str, num: list[str], cat: list[str],
    text_mode: str | None, mode: str,
) -> dict[str, float]:
    data = df.dropna(subset=[target]).copy()
    y = data[target].astype(int).values
    pred = np.zeros(len(data))
    splitter, groups = _split(mode, data)
    for train_idx, test_idx in splitter.split(data, y, groups=groups):
        pipe = Pipeline([
            ("pre", _pre(num, cat, text_mode)),
            ("model", LogisticRegression(max_iter=3000, C=1.0)),
        ])
        pipe.fit(data.iloc[train_idx], y[train_idx])
        pred[test_idx] = pipe.predict_proba(data.iloc[test_idx])[:, 1]
    return {
        "auc": float(roc_auc_score(y, pred)),
        "pr_auc": float(average_precision_score(y, pred)),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path,
                        default=EXP6 / "results" / "static_features.csv")
    parser.add_argument("--current-runs", type=Path,
                        default=EXP6 / "results" / "current_runs.csv")
    parser.add_argument("--examples-runs", type=Path,
                        default=EXP6 / "results" / "example_runs.csv")
    parser.add_argument("--out", type=Path,
                        default=Path(__file__).resolve().parent / "results" / "text_report.json")
    args = parser.parse_args(argv)

    tasks = _load(ROOT / "data" / "task")
    features = pd.read_csv(args.features)
    drop = [c for c in ("task_type", "label", "task_id") if c in features]
    df = tasks.merge(features.drop(columns=drop, errors="ignore"),
                     on="rel", how="left")
    namespace = SimpleNamespace(
        current_runs=args.current_runs,
        examples_runs=args.examples_runs,
        v0001=ROOT / "data" / "harness_task_score" / "harness_v_0001.tsv",
    )
    df = _load_targets(namespace, df)
    df["block"] = df["task_id"].map(_block)
    num = _numeric_columns(df)
    cat = ["task_type"]
    print(f"tasks: {len(df)}, numeric: {len(num)}")

    report: dict[str, Any] = {"tasks": len(df)}
    variants = {"structural": None, "tfidf_word": "word", "tfidf_char": "char"}
    for target, label in (("cost_current_mean", "current v0003 cost"),
                          ("cost_v1_median", "v0001 cost")):
        if target not in df or df[target].notna().sum() < 20:
            continue
        print(f"\n== {label} ==")
        report[target] = {}
        for mode in ("random", "category", "block"):
            for name, text_mode in variants.items():
                metrics = _regression(df, target, num, cat, text_mode, mode)
                report[target][f"{mode}/{name}"] = metrics
                print(f"{mode:9s} {name:14s} MAE={metrics['mae']:7.1f} "
                      f"rho={metrics['spearman']:.3f} R2={metrics['r2']:.3f}")

    print("\n== impossible ==")
    report["impossible"] = {}
    for mode in ("random", "category", "block"):
        for name, text_mode in variants.items():
            metrics = _classification(
                df, "is_impossible_dir", num, cat, text_mode, mode)
            report["impossible"][f"{mode}/{name}"] = metrics
            print(f"{mode:9s} {name:14s} AUC={metrics['auc']:.3f} "
                  f"PR={metrics['pr_auc']:.3f}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
