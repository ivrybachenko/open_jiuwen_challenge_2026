#!/usr/bin/env python3
"""Train first-wave predictors on harness v0002 attempt logs.

The experiment is deliberately restricted to records produced by the current
harness version (``0002``): the cost of a turn depends on prompts, limits and
logging, so mixing versions would teach the model an obsolete cost function.

Targets (measured after the first wave):

* ``remaining_tokens`` -- tokens spent by all later turns of the same run;
* ``remaining_turns``  -- number of later turns (0 or 1 in v0002);
* ``wave2_cost``       -- tokens spent by wave 2, only for tasks that did not
  answer in wave 1;
* ``wave2_any_answer`` -- whether wave 2 produced a non-empty answer;
* ``solvable``         -- synthetic dataset label (solvable / impossible).

Splits are by task, never by run, because several runs of one task would leak
the task.  The tasks that already have v0002 logs are held out as an
external-like test set; the rest are split 60/20/20.

Run with the harness virtualenv (it already has numpy/pandas/scikit-learn)::

    harness/.venv/bin/python \
        research/experiments/0002-first-wave-predictors/train_predictors.py \
        --records data/trajectories/exp0002-shard0/bash_attempts.jsonl \
                  data/trajectories/exp0002-shard1/bash_attempts.jsonl \
                  data/trajectories/exp0002-shard2/bash_attempts.jsonl \
        --external-records data/trajectories/bash_attempts.jsonl
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import warnings
from collections import Counter, defaultdict
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
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    log_loss,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from scipy.stats import spearmanr

warnings.filterwarnings("ignore", category=RuntimeWarning)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TASKS_DIR = ROOT / "data" / "task"
PRIMARY_RUN_PREFIX = "exp0002-full-v0002-20261112-s"
N_JOBS = -1
EXTERNAL_PREFIX = "exp0002-"

CAT_COLS = ["task_type", "answer_kind", "finish_reason", "exit_code_bucket"]

# Lexical markers in the model's own reasoning.  These are deliberately
# hand-written phrase families rather than n-grams: the hypothesis is that
# uncertainty / surprise / contradiction markers carry signal, not the exact
# wording of one synthetic generator.
KEYWORD_PATTERNS = {
    "it_must_work": re.compile(r"\bit\s+must\s+work\b", re.I),
    "must_work": re.compile(r"\bmust\s+work\b", re.I),
    "fine": re.compile(r"\bfine\b", re.I),
    "hmm": re.compile(r"\bhmm+\b", re.I),
    "all_right": re.compile(r"\ball\s+right\b", re.I),
    "wow": re.compile(r"\bwow\b", re.I),
    "contradictory": re.compile(
        r"\bcontradictor(?:y|ily)\b|\bcontradiction\b", re.I
    ),
    "weird": re.compile(r"\bweird\b|\bstrange\b", re.I),
    "wait": re.compile(r"\bwait\b", re.I),
    "actually": re.compile(r"\bactually\b", re.I),
    "double_check": re.compile(r"\bdouble[- ]check\b|\bcheck\s+again\b", re.I),
    "not_sure": re.compile(r"\bnot\s+sure\b|\bunsure\b", re.I),
    "maybe": re.compile(r"\bmaybe\b|\bperhaps\b", re.I),
    "probably": re.compile(r"\bprobably\b|\blikely\b", re.I),
    "i_think": re.compile(r"\bi\s+think\b|\bi\s+believe\b", re.I),
    "seems": re.compile(r"\bseems?\b|\blooks\s+like\b", re.I),
    "stuck": re.compile(r"\bstuck\b", re.I),
    "give_up": re.compile(r"\bgive\s+up\b|\bcan'?t\s+solve\b|\bcannot\s+solve\b", re.I),
    "no_solution": re.compile(r"\bno\s+solution\b|\bimpossible\b|\bunsolvable\b", re.I),
}
KEYWORD_NUM = [
    f"kw_{name}_{suffix}"
    for name in KEYWORD_PATTERNS
    for suffix in ("per100", "present")
]

# Only signals available after the first model turn and its script execution.
TURN_NUM = [
    "reward",
    "first_cost",
    "input_tokens",
    "output_tokens",
    "output_input_ratio",
    "reasoning_output_ratio",
    "reasoning_chars",
    "reasoning_words",
    "reasoning_lines",
    "reasoning_duration_seconds",
    "reasoning_tokens",
    "script_chars",
    "script_lines",
    "script_duration_seconds",
    "output_chars",
    "answer_chars",
    "duration_seconds",
    "hit_token_limit",
    "script_has_python",
    "script_has_file_ops",
    "script_has_write_answer",
    "script_has_tests",
    "script_mentions_impossible",
    "script_timed_out",
    "script_error_present",
    "model_error_present",
    "answer_present",
    "tests_in_overview",
    "reasoning_keyword_impossible",
    "reasoning_keyword_give_up",
    "reasoning_keyword_file_ops",
    "reasoning_keyword_python",
    "reasoning_keyword_write_answer",
    "reasoning_keyword_tests",
]

OVERVIEW_NUM = ["overview_chars", "overview_words", "overview_lines"]

STATIC_NUM = [
    "ins_chars",
    "ins_words",
    "ins_lines",
    "ins_digits",
    "ins_upper",
    "ins_questions",
    "ins_has_test",
    "ins_has_csv",
    "ins_has_json",
    "ins_has_python",
    "ins_has_bash",
    "ins_has_directory",
    "ins_has_impossible",
    "ws_files",
    "ws_bytes",
    "ws_max_file",
    "ws_py",
    "ws_csv",
    "ws_json",
    "ws_txt",
    "ws_has_tests",
]

FEATURE_SETS = {
    "turn": CAT_COLS + TURN_NUM,
    "turn_overview": CAT_COLS + TURN_NUM + OVERVIEW_NUM,
    "turn_keywords": CAT_COLS + TURN_NUM + KEYWORD_NUM,
    "full": CAT_COLS + TURN_NUM + KEYWORD_NUM + OVERVIEW_NUM + STATIC_NUM,
}


def task_cost(rec: dict[str, Any]) -> int:
    f = rec.get("features") or {}
    return int(f.get("output_tokens") or 0) + math.ceil(int(f.get("input_tokens") or 0) / 10)


def load_task_meta(tasks_dir: Path) -> dict[str, dict[str, Any]]:
    meta: dict[str, dict[str, Any]] = {}
    for path in tasks_dir.glob("*/*/*/task.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        rel = path.parent.relative_to(tasks_dir)
        task_type = str(payload.get("task_type") or rel.parts[0])
        solvable = rel.parts[1] == "solvable"
        workspace = path.parent / "workspace"
        meta[str(payload["task_id"])] = {
            "task_id": str(payload["task_id"]),
            "task_type": task_type,
            "solvable": int(solvable),
            "reward": float(payload.get("reward") or 0),
            "instruction": str(payload.get("instruction") or ""),
            "workspace": workspace,
            "task_path": str(rel),
        }
    return meta


def instruction_features(text: str) -> dict[str, float]:
    low = text.lower()
    words = text.split()
    return {
        "ins_chars": len(text),
        "ins_words": len(words),
        "ins_lines": text.count("\n") + 1,
        "ins_digits": sum(ch.isdigit() for ch in text),
        "ins_upper": sum(1 for word in words if word.isupper() and len(word) > 1),
        "ins_questions": text.count("?"),
        "ins_has_test": int("test" in low),
        "ins_has_csv": int("csv" in low),
        "ins_has_json": int("json" in low),
        "ins_has_python": int("python" in low),
        "ins_has_bash": int("bash" in low),
        "ins_has_directory": int("director" in low),
        "ins_has_impossible": int(
            ("impossible" in low) or ("cannot" in low) or ("not possible" in low)
        ),
    }


def workspace_features(workspace: Path) -> dict[str, float]:
    files: list[Path] = []
    if workspace.is_dir():
        for path in workspace.rglob("*"):
            if path.is_file() and not path.is_symlink():
                files.append(path)
    sizes: list[int] = []
    for path in files:
        try:
            sizes.append(path.stat().st_size)
        except OSError:
            sizes.append(0)
    suffixes = Counter(path.suffix.lower() for path in files)
    names = [path.name.lower() for path in files]
    return {
        "ws_files": len(files),
        "ws_bytes": sum(sizes),
        "ws_max_file": max(sizes, default=0),
        "ws_py": suffixes.get(".py", 0),
        "ws_csv": suffixes.get(".csv", 0),
        "ws_json": suffixes.get(".json", 0),
        "ws_txt": suffixes.get(".txt", 0),
        "ws_has_tests": int(
            any(name.startswith("test") and name.endswith(".py") for name in names)
        ),
    }


def read_records(paths: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        if not path.is_file():
            continue
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def keyword_features(rec: dict[str, Any]) -> dict[str, float]:
    """Count hand-written lexical markers in reasoning + content."""
    text = f"{rec.get('reasoning') or ''}\n{rec.get('content') or ''}"
    words = max(1, len(text.split()))
    result: dict[str, float] = {}
    for name, pattern in KEYWORD_PATTERNS.items():
        count = len(pattern.findall(text))
        result[f"kw_{name}_per100"] = 100.0 * count / words
        result[f"kw_{name}_present"] = float(count > 0)
    return result


def build_rows(
    records: list[dict[str, Any]],
    meta: dict[str, dict[str, Any]],
    *,
    source: str,
    correctness: dict[str, bool] | None = None,
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for rec in records:
        task_id = str(rec.get("task_id") or "")
        run_id = str(rec.get("run_id") or "")
        if not task_id or task_id not in meta:
            continue
        groups[(run_id, task_id)].append(rec)

    rows: list[dict[str, Any]] = []
    for (run_id, task_id), group in groups.items():
        group = sorted(
            group,
            key=lambda rec: (int(rec.get("turn") or 0), str(rec.get("logged_at") or "")),
        )
        wave1 = next((rec for rec in group if int(rec.get("wave") or 0) == 1), None)
        if wave1 is None:
            continue
        wave2 = next((rec for rec in group if int(rec.get("wave") or 0) == 2), None)
        info = meta[task_id]
        feature_payload = dict(wave1.get("features") or {})
        total_cost = max(int(rec.get("state_cost") or 0) for rec in group)
        first_cost = int(wave1.get("state_cost") or 0) or task_cost(wave1)
        wave2_cost = 0
        if wave2 is not None:
            wave2_cost = max(0, int(wave2.get("state_cost") or 0) - first_cost)
        remaining_tokens = max(0, total_cost - first_cost)
        remaining_turns = sum(1 for rec in group if int(rec.get("wave") or 0) == 2)
        wave1_kind = str(wave1.get("answer_kind") or "none")
        wave2_kind = str(wave2.get("answer_kind") or "none") if wave2 else "none"
        final_kind = str(group[-1].get("answer_kind") or "none")

        row: dict[str, Any] = {
            "source": source,
            "run_id": run_id,
            "task_id": task_id,
            "task_path": info["task_path"],
            "original_example": int(
                bool(re.match(r"(coding|data_analysis|math|search)/solvable/000[12]$", info["task_path"]))
            ),
            "task_type": info["task_type"],
            "solvable": info["solvable"],
            "reward": info["reward"],
            "wave1_answer_kind": wave1_kind,
            "wave1_answered": int(wave1_kind != "none"),
            "wave2_exists": int(wave2 is not None),
            "wave2_answer_kind": wave2_kind,
            "wave2_any_answer": int(wave2 is not None and wave2_kind != "none"),
            "wave2_non_impossible": int(wave2 is not None and wave2_kind in {"value", "done"}),
            "final_answer_kind": final_kind,
            "remaining_tokens": remaining_tokens,
            "remaining_turns": remaining_turns,
            "wave2_cost": wave2_cost,
            "solved_correctly": (
                None
                if correctness is None or task_id not in correctness
                else int(bool(correctness[task_id]))
            ),
            "wave2_success": (
                None
                if correctness is None or task_id not in correctness
                else int(
                    bool(correctness[task_id])
                    and wave1_kind == "none"
                    and wave2 is not None
                )
            ),
            "first_cost": first_cost,
            "total_cost": total_cost,
            "input_tokens": int(feature_payload.get("input_tokens") or 0),
            "output_tokens": int(feature_payload.get("output_tokens") or 0),
            "overview_chars": len(wave1.get("overview") or ""),
            "overview_words": len((wave1.get("overview") or "").split()),
            "overview_lines": (wave1.get("overview") or "").count("\n") + 1,
            "duration_seconds": float(wave1.get("duration_seconds") or 0),
        }
        # Behavioural features recorded by the harness.
        for key in TURN_NUM:
            if key in {"first_cost", "input_tokens", "output_tokens", "duration_seconds"}:
                continue
            if key == "script_error_present":
                row[key] = int(bool(wave1.get("script_error")))
            elif key == "model_error_present":
                row[key] = int(bool(wave1.get("model_error")))
            else:
                value = feature_payload.get(key)
                if isinstance(value, bool):
                    row[key] = int(value)
                elif isinstance(value, (int, float)):
                    row[key] = float(value)
                elif value is None:
                    row[key] = 0.0
                else:
                    row[key] = float(value) if str(value).strip() else 0.0
        row["answer_kind"] = wave1_kind
        row["finish_reason"] = str(feature_payload.get("finish_reason") or "unknown")
        row["exit_code_bucket"] = _exit_bucket(wave1.get("exit_code"))
        row["output_input_ratio"] = row["output_tokens"] / max(1.0, row["input_tokens"])
        row["reasoning_output_ratio"] = row["reasoning_tokens"] / max(1.0, row["output_tokens"])
        row["script_error_present"] = int(bool(wave1.get("script_error")))
        row["model_error_present"] = int(bool(wave1.get("model_error")))

        row.update(keyword_features(wave1))
        instruction = instruction_features(info["instruction"])
        workspace = workspace_features(info["workspace"])
        row.update(instruction)
        row.update(workspace)
        rows.append(row)
    return rows


def _exit_bucket(value: Any) -> str:
    if value is None:
        return "none"
    try:
        number = int(value)
    except (TypeError, ValueError):
        return "other"
    if number in (0, 1, 2):
        return str(number)
    return "other"


def stratified_task_split(
    df: pd.DataFrame,
    *,
    test_tasks: set[str],
    seed: int,
    train_frac: float = 0.6,
    val_frac: float = 0.2,
) -> dict[str, str]:
    """Split by task, keeping task_type/solvable proportions in each split."""
    tasks = df.drop_duplicates("task_id").copy()
    forced_test = set(tasks.loc[tasks["task_id"].isin(test_tasks), "task_id"])
    rest = tasks.loc[~tasks["task_id"].isin(forced_test)]
    rng = random.Random(seed)
    split: dict[str, str] = {task_id: "test" for task_id in forced_test}
    for _, group in rest.groupby(["task_type", "solvable"], sort=True):
        ids = sorted(group["task_id"].tolist())
        rng.shuffle(ids)
        n = len(ids)
        n_train = max(1, round(n * train_frac)) if n >= 3 else max(1, n - 2)
        n_val = max(1, round(n * val_frac)) if n - n_train >= 2 else max(0, n - n_train - 1)
        for index, task_id in enumerate(ids):
            if index < n_train:
                split[task_id] = "train"
            elif index < n_train + n_val:
                split[task_id] = "val"
            else:
                split[task_id] = "test"
    return split


def vertical_task_split(
    df: pd.DataFrame,
    *,
    train_types: list[str],
    val_type: str,
    test_type: str,
) -> dict[str, str]:
    """Split by task category: train on some types, validate/test on others."""
    split: dict[str, str] = {}
    for task_id, task_type in df.drop_duplicates("task_id")[["task_id", "task_type"]].itertuples(index=False):
        if task_type in train_types:
            split[str(task_id)] = "train"
        elif task_type == val_type:
            split[str(task_id)] = "val"
        elif task_type == test_type:
            split[str(task_id)] = "test"
        else:
            split[str(task_id)] = "train"
    return split


def build_matrix(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    data = df[columns].copy()
    for column in CAT_COLS:
        if column in data:
            data[column] = data[column].fillna("missing").astype(str)
    for column in data.columns:
        if column not in CAT_COLS:
            data[column] = pd.to_numeric(data[column], errors="coerce")
    return data


def make_preprocessor(columns: list[str]) -> ColumnTransformer:
    numeric = [column for column in columns if column not in CAT_COLS]
    categorical = [column for column in columns if column in CAT_COLS]
    return ColumnTransformer(
        [
            (
                "num",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                numeric,
            ),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical,
            ),
        ],
        remainder="drop",
    )


def make_pipeline(columns: list[str], model: Any) -> Pipeline:
    return Pipeline([("pre", make_preprocessor(columns)), ("model", model)])


def regression_metrics(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    y = np.asarray(y, dtype=float)
    pred = np.asarray(pred, dtype=float)
    result = {
        "mae": float(mean_absolute_error(y, pred)),
        "rmse": float(math.sqrt(mean_squared_error(y, pred))),
        "medae": float(np.median(np.abs(y - pred))),
        "bias": float(np.mean(pred - y)),
    }
    if len(y) > 1 and np.std(y) > 0 and np.std(pred) > 0:
        result["r2"] = float(r2_score(y, pred))
        result["spearman"] = float(spearmanr(y, pred).statistic)
    else:
        result["r2"] = float("nan")
        result["spearman"] = float("nan")
    return result


def classification_metrics(y: np.ndarray, prob: np.ndarray) -> dict[str, float]:
    y = np.asarray(y, dtype=int)
    prob = np.asarray(prob, dtype=float)
    pred = (prob >= 0.5).astype(int)
    result = {
        "accuracy": float((pred == y).mean()),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred))
        if len(set(y)) > 1
        else float("nan"),
        "brier": float(brier_score_loss(y, prob)),
        "log_loss": float(log_loss(y, np.clip(prob, 1e-6, 1 - 1e-6), labels=[0, 1])),
        "base_rate": float(y.mean()),
    }
    if len(set(y)) > 1:
        result["roc_auc"] = float(roc_auc_score(y, prob))
        result["average_precision"] = float(average_precision_score(y, prob))
    else:
        result["roc_auc"] = float("nan")
        result["average_precision"] = float("nan")
    return result


def bootstrap_regression(
    y: np.ndarray,
    pred: np.ndarray,
    *,
    n_boot: int = 1000,
    seed: int = 42,
) -> dict[str, list[float]]:
    rng = np.random.default_rng(seed)
    keys = ["mae", "rmse", "medae", "spearman"]
    samples: dict[str, list[float]] = {key: [] for key in keys}
    n = len(y)
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        metrics = regression_metrics(y[idx], pred[idx])
        for key in keys:
            value = metrics.get(key, float("nan"))
            if not math.isnan(value):
                samples[key].append(value)
    return {
        key: [float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))]
        for key, values in samples.items()
        if values
    }


def bootstrap_classification(
    y: np.ndarray,
    prob: np.ndarray,
    *,
    n_boot: int = 1000,
    seed: int = 42,
) -> dict[str, list[float]]:
    rng = np.random.default_rng(seed)
    keys = ["roc_auc", "average_precision", "accuracy", "brier"]
    samples: dict[str, list[float]] = {key: [] for key in keys}
    n = len(y)
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if len(set(y[idx])) < 2:
            continue
        metrics = classification_metrics(y[idx], prob[idx])
        for key in keys:
            value = metrics.get(key, float("nan"))
            if not math.isnan(value):
                samples[key].append(value)
    return {
        key: [float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))]
        for key, values in samples.items()
        if values
    }


def calibration_report(y: np.ndarray, prob: np.ndarray) -> dict[str, Any]:
    eps = 1e-6
    prob = np.clip(np.asarray(prob, dtype=float), eps, 1 - eps)
    logits = np.log(prob / (1 - prob)).reshape(-1, 1)
    slope = intercept = float("nan")
    if len(set(y)) > 1:
        model = LogisticRegression(max_iter=1000).fit(logits, y)
        slope = float(model.coef_[0, 0])
        intercept = float(model.intercept_[0])
    bins = []
    edges = np.quantile(prob, np.linspace(0, 1, 6))
    edges = np.unique(edges)
    for low, high in zip(edges[:-1], edges[1:]):
        mask = (prob >= low) & (prob <= high if high == edges[-1] else prob < high)
        if mask.sum() == 0:
            continue
        bins.append(
            {
                "low": float(low),
                "high": float(high),
                "n": int(mask.sum()),
                "predicted": float(prob[mask].mean()),
                "observed": float(np.asarray(y)[mask].mean()),
            }
        )
    return {"slope": slope, "intercept": intercept, "bins": bins}


def fit_regression_candidates(
    df: pd.DataFrame,
    *,
    target: str,
    columns: list[str],
    split: dict[str, str],
) -> dict[str, Any]:
    masks = {name: df["task_id"].map(split) == name for name in ("train", "val", "test")}
    X = build_matrix(df, columns)
    y = df[target].astype(float).to_numpy()
    train = masks["train"].to_numpy()
    val = masks["val"].to_numpy()
    test = masks["test"].to_numpy()
    if train.sum() < 2 or val.sum() < 1 or test.sum() < 1:
        return {"skipped": f"empty split: train={int(train.sum())}, val={int(val.sum())}, test={int(test.sum())}"}

    baselines: dict[str, Any] = {}
    median = float(np.median(y[train]))
    baseline_pred = {
        "global_median": np.full(len(df), median),
        "category_median": np.zeros(len(df)),
    }
    category_median = (
        df.loc[train].groupby("task_type")[target].median().to_dict()
    )
    for position, (_, row) in enumerate(df.iterrows()):
        baseline_pred["category_median"][position] = category_median.get(
            row["task_type"], median
        )
    if "answer_present" in df:
        answered = df["answer_present"].astype(float).to_numpy()
        if target == "remaining_turns":
            baseline_pred["answer_present_rule"] = 1.0 - answered
            if "answer_kind" in df:
                baseline_pred["answer_kind_rule"] = (
                    df["answer_kind"].isin(["none", "impossible"]).astype(float).to_numpy()
                )
        elif target in {"remaining_tokens", "wave2_cost"}:
            unanswered = y[train][df.loc[train, "answer_present"].to_numpy() == 0]
            unanswered_median = float(np.median(unanswered)) if len(unanswered) else median
            baseline_pred["zero_if_answered_else_median"] = np.where(
                answered > 0, 0.0, unanswered_median
            )
    for name, pred in baseline_pred.items():
        baselines[name] = {
            "val": regression_metrics(y[val], pred[val]),
            "test": regression_metrics(y[test], pred[test]),
        }

    candidates = [
        ("ridge", Ridge(), {"alpha": [0.1, 1.0, 10.0, 100.0]}, False),
        (
            "random_forest",
            RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=N_JOBS),
            {
                "min_samples_leaf": [1, 4, 8],
                "max_features": [0.5, 0.8],
            },
            False,
        ),
        (
            "random_forest_log",
            RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=N_JOBS),
            {
                "min_samples_leaf": [1, 4, 8],
                "max_features": [0.5, 0.8],
            },
            True,
        ),
        (
            "hist_gradient_boosting",
            HistGradientBoostingRegressor(max_iter=200, random_state=42),
            {
                "learning_rate": [0.03, 0.06, 0.1],
                "max_leaf_nodes": [7, 15, 31],
            },
            False,
        ),
        (
            "hist_gradient_boosting_log",
            HistGradientBoostingRegressor(max_iter=200, random_state=42),
            {
                "learning_rate": [0.03, 0.06, 0.1],
                "max_leaf_nodes": [7, 15, 31],
            },
            True,
        ),
    ]

    candidate_results: dict[str, Any] = {}
    best: dict[str, Any] | None = None
    for name, model, grid, log_target in candidates:
        best_for_name: dict[str, Any] | None = None
        for params in _param_grid(grid):
            candidate = model
            if params:
                candidate = clone_model(model).set_params(**params)
            pipeline = make_pipeline(columns, candidate)
            y_train = np.log1p(y[train]) if log_target else y[train]
            pipeline.fit(X[train], y_train)
            val_pred = pipeline.predict(X[val])
            if log_target:
                val_pred = np.expm1(val_pred)
            val_pred = np.clip(val_pred, 0, None)
            score = mean_absolute_error(y[val], val_pred)
            entry = {
                "params": params,
                "log_target": log_target,
                "val_mae": float(score),
                "val": regression_metrics(y[val], val_pred),
            }
            if best_for_name is None or entry["val_mae"] < best_for_name["val_mae"]:
                best_for_name = entry
        # Refit the best params of this family and score the test split once.
        pipeline = make_pipeline(columns, _clone_with_params(model, best_for_name["params"]))
        y_train = np.log1p(y[train]) if log_target else y[train]
        pipeline.fit(X[train], y_train)
        for split_name, mask in (("val", val), ("test", test)):
            pred = pipeline.predict(X[mask])
            if log_target:
                pred = np.expm1(pred)
            pred = np.clip(pred, 0, None)
            if split_name == "test":
                entry = dict(best_for_name)
                entry["test"] = regression_metrics(y[test], pred)
                entry["test_ci"] = bootstrap_regression(y[test], pred)
                entry["pipeline"] = pipeline
                entry["pred_test"] = pred
                entry["model_name"] = name
                candidate_results[name] = entry
                if best is None or entry["val_mae"] < best["val_mae"]:
                    best = entry
    return {"baselines": baselines, "candidates": candidate_results, "best": best}


def _param_grid(grid: dict[str, list[Any]]) -> list[dict[str, Any]]:
    if not grid:
        return [{}]
    keys = list(grid)
    values = [grid[key] for key in keys]
    import itertools

    return [dict(zip(keys, combo)) for combo in itertools.product(*values)]


def clone_model(model: Any) -> Any:
    from sklearn.base import clone

    return clone(model)


def _clone_with_params(model: Any, params: dict[str, Any]) -> Any:
    candidate = clone_model(model)
    if params:
        candidate.set_params(**params)
    return candidate


def fit_classification_candidates(
    df: pd.DataFrame,
    *,
    target: str,
    columns: list[str],
    split: dict[str, str],
) -> dict[str, Any]:
    masks = {name: df["task_id"].map(split) == name for name in ("train", "val", "test")}
    X = build_matrix(df, columns)
    y = df[target].astype(int).to_numpy()
    train = masks["train"].to_numpy()
    val = masks["val"].to_numpy()
    test = masks["test"].to_numpy()
    if train.sum() < 2 or val.sum() < 1 or test.sum() < 1:
        return {"skipped": f"empty split: train={int(train.sum())}, val={int(val.sum())}, test={int(test.sum())}"}
    if len(set(y[train])) < 2:
        return {"skipped": "one class in train"}

    baselines: dict[str, Any] = {}
    prior = float(y[train].mean())
    baseline_prob = {
        "global_prior": np.full(len(df), prior),
        "category_prior": np.zeros(len(df)),
    }
    category_prior = df.loc[train].groupby("task_type")[target].mean().to_dict()
    for position, (_, row) in enumerate(df.iterrows()):
        baseline_prob["category_prior"][position] = category_prior.get(row["task_type"], prior)
    for name, prob in baseline_prob.items():
        baselines[name] = {
            "val": classification_metrics(y[val], prob[val]),
            "test": classification_metrics(y[test], prob[test]),
        }

    candidates = [
        (
            "logistic_regression",
            LogisticRegression(
                max_iter=3000, class_weight="balanced", random_state=42
            ),
            {"C": [0.03, 0.1, 0.3, 1.0, 3.0]},
        ),
        (
            "random_forest",
            RandomForestClassifier(
                n_estimators=300, class_weight="balanced", random_state=42, n_jobs=N_JOBS
            ),
            {
                "min_samples_leaf": [1, 4, 8],
                "max_features": [0.5, 0.8],
            },
        ),
        (
            "hist_gradient_boosting",
            HistGradientBoostingClassifier(
                max_iter=200, class_weight="balanced", random_state=42
            ),
            {
                "learning_rate": [0.03, 0.06, 0.1],
                "max_leaf_nodes": [7, 15, 31],
            },
        ),
    ]
    candidate_results: dict[str, Any] = {}
    best: dict[str, Any] | None = None
    for name, model, grid in candidates:
        best_for_name: dict[str, Any] | None = None
        for params in _param_grid(grid):
            pipeline = make_pipeline(columns, _clone_with_params(model, params))
            pipeline.fit(X[train], y[train])
            val_prob = pipeline.predict_proba(X[val])[:, 1]
            score = roc_auc_score(y[val], val_prob) if len(set(y[val])) > 1 else 0.0
            entry = {
                "params": params,
                "val_roc_auc": float(score),
                "val": classification_metrics(y[val], val_prob),
            }
            if best_for_name is None or entry["val_roc_auc"] > best_for_name["val_roc_auc"]:
                best_for_name = entry
        pipeline = make_pipeline(columns, _clone_with_params(model, best_for_name["params"]))
        pipeline.fit(X[train], y[train])
        val_prob = pipeline.predict_proba(X[val])[:, 1]
        test_prob = pipeline.predict_proba(X[test])[:, 1]
        entry = dict(best_for_name)
        entry["val"] = classification_metrics(y[val], val_prob)
        entry["test"] = classification_metrics(y[test], test_prob)
        entry["test_ci"] = bootstrap_classification(y[test], test_prob)
        entry["calibration"] = calibration_report(y[test], test_prob)
        entry["pipeline"] = pipeline
        entry["pred_test"] = test_prob
        entry["model_name"] = name
        candidate_results[name] = entry
        if best is None or entry["val_roc_auc"] > best["val_roc_auc"]:
            best = entry
    return {"baselines": baselines, "candidates": candidate_results, "best": best}


def permutation_report(
    best: dict[str, Any],
    df: pd.DataFrame,
    columns: list[str],
    *,
    target: str,
    task: str,
    seed: int,
) -> list[dict[str, Any]]:
    mask = df["task_id"].map(best["_split"]) == "test"
    if mask.sum() < 5 or "pipeline" not in best:
        return []
    X = build_matrix(df.loc[mask], columns)
    y = df.loc[mask, target].to_numpy()
    pipeline = best["pipeline"]
    if task == "regression":
        scoring = "neg_mean_absolute_error"
    else:
        scoring = "neg_brier_score"
    result = permutation_importance(
        pipeline,
        X,
        y,
        scoring=scoring,
        n_repeats=8,
        random_state=seed,
        n_jobs=N_JOBS,
    )
    pairs = sorted(
        zip(columns, result.importances_mean, result.importances_std),
        key=lambda item: -item[1],
    )
    return [
        {"feature": name, "mean": float(mean), "std": float(std)}
        for name, mean, std in pairs[:15]
    ]


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            (key if isinstance(key, str) else str(key)): json_safe(item)
            for key, item in value.items()
            if key not in {"pipeline", "pred_test", "_split"}
        }
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", nargs="+", required=True, type=Path)
    parser.add_argument("--external-records", nargs="*", default=[], type=Path)
    parser.add_argument("--tasks-dir", type=Path, default=DEFAULT_TASKS_DIR)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "results",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--bootstrap", type=int, default=300)
    parser.add_argument(
        "--skip-importance",
        action="store_true",
        help="Skip permutation importance (faster for split comparisons).",
    )
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=-1,
        help="Threads for forests/permutation importance; use 1 when running "
        "several split variants in parallel.",
    )
    parser.add_argument("--n-permutation-repeats", type=int, default=20)
    parser.add_argument(
        "--correctness",
        type=Path,
        default=None,
        help="JSON mapping task_id -> bool from the answer evaluator.",
    )
    parser.add_argument(
        "--primary-run-prefix",
        default=PRIMARY_RUN_PREFIX,
    )
    parser.add_argument(
        "--split-mode",
        choices=("horizontal", "vertical"),
        default="horizontal",
        help="horizontal = random task split within all categories; "
        "vertical = train on some categories, validate/test on others.",
    )
    parser.add_argument(
        "--vertical-train-types",
        nargs="+",
        default=["coding", "data_analysis"],
    )
    parser.add_argument("--vertical-val-type", default="math")
    parser.add_argument("--vertical-test-type", default="search")
    args = parser.parse_args(argv)
    global N_JOBS
    N_JOBS = args.n_jobs

    args.out.mkdir(parents=True, exist_ok=True)
    meta = load_task_meta(args.tasks_dir)
    correctness: dict[str, bool] | None = None
    if args.correctness is not None:
        raw = json.loads(args.correctness.read_text(encoding="utf-8"))
        correctness = {str(key): bool(value) for key, value in raw.items()}

    primary_records = [
        rec
        for rec in read_records(args.records)
        if str(rec.get("run_id") or "").startswith(args.primary_run_prefix)
    ]
    external_records = [
        rec
        for rec in read_records(args.external_records)
        if not str(rec.get("run_id") or "").startswith(EXTERNAL_PREFIX)
    ]
    primary = pd.DataFrame(
        build_rows(primary_records, meta, source="primary", correctness=correctness)
    )
    external = pd.DataFrame(build_rows(external_records, meta, source="external"))
    if primary.empty:
        raise SystemExit("no primary rows; check --records and --primary-run-prefix")

    # Tasks already represented in external logs are forced to test, so the
    # external evaluation is not contaminated by the same task in training.
    external_task_ids = set(external["task_id"]) if not external.empty else set()
    if args.split_mode == "horizontal":
        split = stratified_task_split(
            primary, test_tasks=external_task_ids, seed=args.seed
        )
    else:
        split = vertical_task_split(
            primary,
            train_types=args.vertical_train_types,
            val_type=args.vertical_val_type,
            test_type=args.vertical_test_type,
        )
    primary["split"] = primary["task_id"].map(split)

    # Conditional frame for tasks that need wave 2.
    conditional = primary.loc[
        (primary["wave1_answered"] == 0) & (primary["wave2_exists"] == 1)
    ].copy()

    data_summary = {
        "primary_rows": int(len(primary)),
        "primary_tasks": int(primary["task_id"].nunique()),
        "primary_runs": int(primary["run_id"].nunique()),
        "external_rows": int(len(external)),
        "external_tasks": int(external["task_id"].nunique()) if not external.empty else 0,
        "external_task_ids": sorted(external_task_ids),
        "by_type_solvable": {
            f"{key[0]}/{key[1]}": int(value)
            for key, value in primary.groupby(["task_type", "solvable"]).size().items()
        },
        "targets": {},
    }

    targets = [
        ("remaining_tokens", primary, "regression"),
        ("remaining_turns", primary, "regression"),
        ("wave2_cost", conditional, "regression"),
        ("solvable", primary, "classification"),
        ("wave2_any_answer", conditional, "classification"),
    ]
    if "solved_correctly" in primary and primary["solved_correctly"].notna().any():
        primary = primary.copy()
        primary["solved_correctly"] = primary["solved_correctly"].astype(int)
        targets.append(("solved_correctly", primary, "classification"))
    if "wave2_success" in conditional and conditional["wave2_success"].notna().any():
        conditional = conditional.copy()
        conditional["wave2_success"] = conditional["wave2_success"].astype(int)
        targets.append(("wave2_success", conditional, "classification"))

    data_summary["targets"] = {
        target: {
            "mean": float(frame[target].mean()),
            "median": float(frame[target].median()),
            "std": float(frame[target].std()),
            "min": float(frame[target].min()),
            "max": float(frame[target].max()),
            "zero_share": float((frame[target] == 0).mean()),
            "n": int(len(frame)),
        }
        for target, frame, _ in targets
    }

    results: dict[str, Any] = {
        "data": data_summary,
        "split": {
            "mode": args.split_mode,
            "seed": args.seed,
            "vertical_train_types": args.vertical_train_types,
            "vertical_val_type": args.vertical_val_type,
            "vertical_test_type": args.vertical_test_type,
            "tasks": {},
            "rows": json_safe(primary["split"].value_counts().to_dict()),
            "tasks_by_type_and_split": {
                f"{key[0]}/{key[1]}": int(value)
                for key, value in primary.drop_duplicates("task_id")
                .groupby(["task_type", "split"])
                .size()
                .items()
            },
        },
        "primary": {},
    }
    # defaultdict is not JSON-safe through Counter.values; replace explicitly.
    results["split"]["tasks"] = {
        "train": sum(1 for value in split.values() if value == "train"),
        "val": sum(1 for value in split.values() if value == "val"),
        "test": sum(1 for value in split.values() if value == "test"),
    }

    for target, frame, task in targets:
        frame = frame.copy()
        frame["_split"] = frame["task_id"].map(split)
        target_results: dict[str, Any] = {}
        for feature_set, columns in FEATURE_SETS.items():
            if task == "regression":
                fit = fit_regression_candidates(
                    frame, target=target, columns=columns, split=split
                )
            else:
                fit = fit_classification_candidates(
                    frame, target=target, columns=columns, split=split
                )
            if "skipped" in fit:
                target_results[feature_set] = fit
                continue
            best = fit["best"]
            if best is not None:
                best["_split"] = split
                if feature_set != "turn" and not args.skip_importance:
                    best["importance"] = permutation_report(
                        best,
                        frame,
                        columns,
                        target=target,
                        task=task,
                        seed=args.seed,
                    )
            target_results[feature_set] = {
                "n_rows": int(len(frame)),
                "n_tasks": int(frame["task_id"].nunique()),
                "baselines": fit["baselines"],
                "best": best,
                "candidates": {
                    name: {key: value for key, value in entry.items() if key not in {"pipeline", "pred_test"}}
                    for name, entry in fit["candidates"].items()
                },
            }
        results["primary"][target] = target_results

    # External-like evaluation: prior v0002 logs on tasks forced to the test
    # split.  The model is trained on the primary train tasks and never sees
    # these tasks; the external rows are different runs of the same tasks.
    external_results: dict[str, Any] = {}
    if not external.empty:
        external_conditional = external.loc[
            (external["wave1_answered"] == 0) & (external["wave2_exists"] == 1)
        ].copy()
        conditional_targets = {"wave2_cost", "wave2_any_answer", "wave2_success"}
        for target, train_frame, task in targets:
            if target not in external.columns or external[target].isna().all():
                continue
            base_external = external.loc[
                external["task_id"].map(split) == "test"
            ]
            eval_rows = (
                base_external.loc[
                    (base_external["wave1_answered"] == 0)
                    & (base_external["wave2_exists"] == 1)
                ]
                if target in conditional_targets
                else base_external
            ).copy()
            if eval_rows.empty:
                continue
            train_frame = train_frame.copy()
            train_mask = train_frame["task_id"].map(split) == "train"
            external_results[target] = {}
            for feature_set, columns in FEATURE_SETS.items():
                primary_fit = results["primary"][target][feature_set]
                best = primary_fit.get("best")
                if not best:
                    continue
                if task == "regression":
                    model = _recreate_regressor(best)
                    pipeline = make_pipeline(columns, model)
                    y_train = train_frame.loc[train_mask, target].astype(float)
                    if best.get("log_target"):
                        y_train = np.log1p(y_train)
                    pipeline.fit(
                        build_matrix(train_frame.loc[train_mask], columns), y_train
                    )
                    pred = pipeline.predict(build_matrix(eval_rows, columns))
                    if best.get("log_target"):
                        pred = np.expm1(pred)
                    pred = np.clip(pred, 0, None)
                    eval_sets = {"all": eval_rows}
                    if "original_example" in eval_rows:
                        examples = eval_rows.loc[eval_rows["original_example"] == 1]
                        if not examples.empty:
                            eval_sets["original_examples"] = examples
                    subsets = {}
                    for subset_name, subset in eval_sets.items():
                        subset_positions = [
                            eval_rows.index.get_loc(index) for index in subset.index
                        ]
                        subsets[subset_name] = {
                            "n": int(len(subset)),
                            "metrics": regression_metrics(
                                subset[target].astype(float).to_numpy(),
                                pred[subset_positions],
                            ),
                        }
                    external_results[target][feature_set] = subsets
                else:
                    model = _recreate_classifier(best)
                    pipeline = make_pipeline(columns, model)
                    pipeline.fit(
                        build_matrix(train_frame.loc[train_mask], columns),
                        train_frame.loc[train_mask, target].astype(int),
                    )
                    prob = pipeline.predict_proba(build_matrix(eval_rows, columns))[:, 1]
                    eval_sets = {"all": eval_rows}
                    if "original_example" in eval_rows:
                        examples = eval_rows.loc[eval_rows["original_example"] == 1]
                        if not examples.empty:
                            eval_sets["original_examples"] = examples
                    subsets = {}
                    for subset_name, subset in eval_sets.items():
                        subset_positions = [
                            eval_rows.index.get_loc(index) for index in subset.index
                        ]
                        subsets[subset_name] = {
                            "n": int(len(subset)),
                            "metrics": classification_metrics(
                                subset[target].astype(int).to_numpy(),
                                prob[subset_positions],
                            ),
                        }
                    external_results[target][feature_set] = subsets
    results["external"] = external_results

    # Save the row-level dataset and predictions for the best primary models.
    public_columns = [
        column
        for column in primary.columns
        if not column.startswith("_")
    ]
    primary[public_columns].to_csv(args.out / "dataset.csv", index=False)
    if not external.empty:
        external_columns = [column for column in public_columns if column in external.columns]
        external[external_columns].to_csv(
            args.out / "external_dataset.csv", index=False
        )

    (args.out / "results.json").write_text(
        json.dumps(json_safe(results), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_summary(results, args.out / "summary.md")
    print(f"wrote {args.out / 'results.json'}")
    print(f"wrote {args.out / 'summary.md'}")
    return 0


def _recreate_regressor(best: dict[str, Any]) -> Any:
    name = best["model_name"]
    params = best.get("params") or {}
    if name == "ridge":
        model: Any = Ridge()
    elif name in {"random_forest", "random_forest_log"}:
        model = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=N_JOBS)
    elif name in {"hist_gradient_boosting", "hist_gradient_boosting_log"}:
        model = HistGradientBoostingRegressor(max_iter=200, random_state=42)
    else:
        raise ValueError(name)
    if params:
        model.set_params(**params)
    return model


def _recreate_classifier(best: dict[str, Any]) -> Any:
    name = best["model_name"]
    params = best.get("params") or {}
    if name == "logistic_regression":
        model: Any = LogisticRegression(max_iter=3000, class_weight="balanced", random_state=42)
    elif name == "random_forest":
        model = RandomForestClassifier(
            n_estimators=300, class_weight="balanced", random_state=42, n_jobs=N_JOBS
        )
    elif name == "hist_gradient_boosting":
        model = HistGradientBoostingClassifier(
            max_iter=200, class_weight="balanced", random_state=42
        )
    else:
        raise ValueError(name)
    if params:
        model.set_params(**params)
    return model


def write_summary(results: dict[str, Any], path: Path) -> None:
    lines: list[str] = ["# Результаты: предсказатели первой волны", ""]
    data = results["data"]
    lines += [
        f"Основной набор: {data['primary_rows']} строк, "
        f"{data['primary_tasks']} задач, {data['primary_runs']} прогонов.",
        f"Внешний набор: {data['external_rows']} строк, "
        f"{data['external_tasks']} задач.",
        "",
        "## Разбиение",
        "",
        f"Задачи: train={results['split']['tasks']['train']}, "
        f"val={results['split']['tasks']['val']}, "
        f"test={results['split']['tasks']['test']}.",
        f"Строки: {results['split']['rows']}.",
        "",
    ]
    for target, target_data in results["primary"].items():
        lines.append(f"## {target}")
        lines.append("")
        lines.append("| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |")
        lines.append("| --- | --- | ---: | ---: | ---: |")
        for feature_set, entry in target_data.items():
            best = entry.get("best")
            if not best:
                continue
            if "val_mae" in best:
                val = best["val_mae"]
                test = best.get("test", {}).get("mae", float("nan"))
                extra = best.get("test", {}).get("r2", float("nan"))
                lines.append(
                    f"| {feature_set} | {best['model_name']} | "
                    f"{val:.1f} | {test:.1f} | {extra:.3f} |"
                )
            else:
                val = best.get("val_roc_auc", float("nan"))
                test = best.get("test", {}).get("roc_auc", float("nan"))
                extra = best.get("test", {}).get("average_precision", float("nan"))
                lines.append(
                    f"| {feature_set} | {best['model_name']} | "
                    f"{val:.3f} | {test:.3f} | {extra:.3f} |"
                )
        lines.append("")
    lines.append("## Внешняя проверка")
    lines.append("")
    for target, target_data in results.get("external", {}).items():
        lines.append(f"### {target}")
        lines.append("")
        for feature_set, entry in target_data.items():
            for subset_name, subset in entry.items():
                metrics = subset.get("metrics", {})
                lines.append(
                    f"- {feature_set}/{subset_name}: n={subset['n']}, "
                    f"`{json.dumps(metrics, ensure_ascii=False)}`"
                )
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
