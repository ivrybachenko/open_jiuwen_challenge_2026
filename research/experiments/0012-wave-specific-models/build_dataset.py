#!/usr/bin/env python3
"""Build a multi-wave turn dataset with evaluator correctness labels.

Sources
-------
* ``research/experiments/**/traj/bash_attempts.jsonl`` -- repeated runs of the
  32-task research set; labels come from ``turn_groups.csv`` (0007).
* ``data/trajectories/bash_attempts.jsonl`` -- evaluation runs on the example
  set and a few extra tasks; labels are reconstructed from ``task.json`` for
  exact checks and from ``out/reports/*.json`` for unittest checks.
* ``data/trajectories/exp0002-shard*/bash_attempts.jsonl`` -- one wave per
  task; labels from ``results/correctness.json`` of experiment 0002.

The output is one row per turn.  Besides the shipped feature set it contains
group-level labels and the answer produced by that turn, so wave-specific
models can be compared on the same rows.

Usage::

    harness/.venv/bin/python \
      research/experiments/0012-wave-specific-models/build_dataset.py
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = Path(__file__).resolve().parent

MODEL_META = (
    ROOT / "harness" / "src" / "harness" / "solving" / "success_predictors"
    / "models" / "online_model.json"
)
NUMERIC = json.loads(MODEL_META.read_text(encoding="utf-8"))["numeric_features"]
CATEGORICAL = json.loads(MODEL_META.read_text(encoding="utf-8"))[
    "categorical_features"
]


# ---------------------------------------------------------------------------
# Task metadata and answer checks
# ---------------------------------------------------------------------------
def _clean_text(text: str | None) -> str:
    value = (text or "").strip()
    if value.startswith("```") and value.endswith("```"):
        value = value.strip("`").strip()
        lines = value.splitlines()
        if len(lines) >= 2 and not lines[0].strip() and not lines[-1].strip():
            value = "\n".join(lines[1:-1]).strip()
    return value


def _parse_int(text: str | None) -> int | None:
    if text is None:
        return None
    cleaned = _clean_text(text)
    candidate = (
        cleaned.replace(",", "").replace("_", "").replace(" ", "").rstrip(".")
    )
    if re.fullmatch(r"[+-]?\d+", candidate):
        return int(candidate)
    numbers = re.findall(r"(?<![\w.])[+-]?\d+(?!\w)(?!\.\d)", cleaned)
    if len(numbers) == 1:
        return int(numbers[0].replace(",", ""))
    return None


def _norm_str(text: str | None) -> str:
    value = " ".join(_clean_text(text).split())
    return value.strip(".,;:!?").casefold()


def numeric_value(features: dict[str, Any], name: str) -> float:
    """Mirror the adapter in ``success_predictors.model``."""
    if name == "timed_out":
        value = features.get("timed_out", features.get("script_timed_out", 0.0))
    elif name == "script_error":
        value = features.get("script_error", 0.0)
        if isinstance(value, str):
            value = len(value)
    else:
        value = features.get(name, 0.0)
    try:
        return float(value) if value is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def exact_correct(meta: dict[str, Any], answer: str | None) -> bool | None:
    """Return True/False for exact checks and None when the check is unknown."""
    if not meta.get("solvable", True):
        return False
    if answer is None or not str(answer).strip():
        return False
    check = (meta.get("check") or "").strip().lower()
    expected = meta.get("expected")
    if check == "exact_int":
        return _parse_int(expected) == _parse_int(answer)
    if check in {"exact_str", "exact_string", "exact_text"}:
        return _norm_str(expected) == _norm_str(answer)
    return None


def load_repo_metadata() -> dict[str, dict[str, Any]]:
    meta: dict[str, dict[str, Any]] = {}
    for path in sorted(
        (ROOT / "data" / "task").glob("*/*/*/task.json")
    ) + sorted(
        (ROOT / "challenge_info" / "task-examples").glob("*/task.json")
    ):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        parts = path.parts
        payload["_solvable"] = (
            "impossible" not in parts if "task-examples" not in parts else True
        )
        payload["_rel"] = (
            "/".join(parts[-4:-1])
            if "task-examples" not in parts
            else path.parent.name
        )
        meta[str(payload.get("task_id"))] = payload
    return meta


def _meta_from_task_root(record: dict[str, Any]) -> dict[str, Any] | None:
    path = Path(record.get("task_root", "")) / "task.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    payload["_solvable"] = payload.get(
        "solvable", not payload.get("impossible", False)
    )
    payload["_rel"] = str(payload.get("task_id", ""))
    return payload


def load_report_labels() -> dict[tuple[str, str], bool]:
    labels: dict[tuple[str, str], bool] = {}
    for path in glob.glob(str(ROOT / "out" / "reports" / "*.json")):
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        command = (payload.get("harness") or {}).get("command") or []
        run_id = (
            command[command.index("--run-id") + 1]
            if "--run-id" in command
            else None
        )
        if payload.get("task_id") and run_id:
            labels[(run_id, str(payload["task_id"]))] = bool(
                payload.get("solved")
            )
        for task in payload.get("tasks") or []:
            if isinstance(task, dict) and task.get("task_id") and run_id:
                labels[(run_id, str(task["task_id"]))] = bool(
                    task.get("solved")
                )
    return labels


def load_turn_group_labels() -> dict[tuple[str, str], bool]:
    path = (
        ROOT / "research" / "experiments"
        / "0007-predict-remaining-cost-during-solve" / "results"
        / "turn_groups.csv"
    )
    frame = pd.read_csv(path)
    return {
        (str(row.run_id), str(row.task_id)): bool(row.correct)
        for row in frame.itertuples()
    }


def load_fresh_run_labels() -> dict[tuple[str, str], bool]:
    """Labels from runs collected by ``run_experiment.py`` in this folder."""
    labels: dict[tuple[str, str], bool] = {}
    base = ROOT / "research" / "experiments" / "0012-wave-specific-models" / "results"
    for path in base.glob("**/summary.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        run_id = str(payload.get("run_id") or "")
        if not run_id:
            continue
        # A failed run (zero cost, no model answers) must not enter the
        # dataset as a set of all-negative labels.
        if float((payload.get("summary") or {}).get("cost") or 0) <= 0:
            continue
        for task in payload.get("tasks") or []:
            if isinstance(task, dict) and task.get("task_id") is not None:
                labels[(run_id, str(task["task_id"]))] = bool(
                    task.get("solved")
                )
    return labels


def load_failed_fresh_runs() -> set[str]:
    """Run ids whose summary says the model was never called."""
    failed: set[str] = set()
    base = ROOT / "research" / "experiments" / "0012-wave-specific-models" / "results"
    for path in base.glob("**/summary.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        run_id = str(payload.get("run_id") or "")
        if run_id and float((payload.get("summary") or {}).get("cost") or 0) <= 0:
            failed.add(run_id)
    return failed


def load_exp0002_labels() -> dict[str, bool]:
    path = (
        ROOT / "research" / "experiments" / "0002-first-wave-predictors"
        / "results" / "correctness.json"
    )
    return {
        str(key): bool(value)
        for key, value in json.loads(path.read_text(encoding="utf-8")).items()
    }


# ---------------------------------------------------------------------------
# Trajectory loading
# ---------------------------------------------------------------------------
def _trajectory_sources() -> list[tuple[Path, str]]:
    sources: list[tuple[Path, str]] = []
    for path in sorted(
        (ROOT / "research" / "experiments").rglob("bash_attempts.jsonl")
    ):
        if path.parent.name == "traj":
            sources.append((path, "research"))
    raw = ROOT / "data" / "trajectories" / "bash_attempts.jsonl"
    if raw.is_file():
        sources.append((raw, "evaluation"))
    for path in sorted(
        (ROOT / "data" / "trajectories").glob("exp0002-shard*/bash_attempts.jsonl")
    ):
        sources.append((path, "exp0002"))
    return sources


def _read_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def build() -> pd.DataFrame:
    repo_meta = load_repo_metadata()
    report_labels = load_report_labels()
    group_labels = load_turn_group_labels()
    fresh_labels = load_fresh_run_labels()
    failed_runs = load_failed_fresh_runs()
    exp0002_labels = load_exp0002_labels()

    rows: list[dict[str, Any]] = []
    seen_runs: set[str] = set()
    for path, source_kind in _trajectory_sources():
        records = _read_records(path)
        groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for record in records:
            run_id = str(record.get("run_id", ""))
            task_id = str(record.get("task_id", ""))
            if not run_id or not task_id:
                continue
            groups[(run_id, task_id)].append(record)
        for (run_id, task_id), turns in groups.items():
            if run_id in failed_runs:
                continue
            turns.sort(
                key=lambda item: (
                    int(item.get("wave", 0) or 0),
                    int(item.get("turn", 0) or 0),
                )
            )
            first = turns[0]
            meta = repo_meta.get(task_id)
            if meta is None:
                meta = _meta_from_task_root(first)
            if meta is None:
                continue
            # The two evaluation shards and research runs have unique ids, but
            # a copied trajectory could appear twice; keep the first copy.
            group_key = (run_id, task_id)
            if run_id in seen_runs and source_kind != "exp0002":
                # Do not deduplicate by run alone: evaluation runs are unique.
                pass

            check = str(meta.get("check") or "").lower()
            # Prefer the evaluator label recorded for the experiment.
            if group_key in fresh_labels:
                final_correct: bool | None = fresh_labels[group_key]
                label_source = "fresh_run"
            elif group_key in group_labels:
                final_correct: bool | None = group_labels[group_key]
                label_source = "turn_groups"
            elif source_kind == "exp0002" and task_id in exp0002_labels:
                final_correct = exp0002_labels[task_id]
                label_source = "exp0002"
            elif (
                meta.get("_solvable") is False
                or str(meta.get("solvable", True)).lower() == "false"
            ):
                final_correct = False
                label_source = "unsolvable"
            elif check in {"unittest", "hidden_unittest"}:
                final_correct = report_labels.get(group_key)
                label_source = (
                    "report" if final_correct is not None else "unknown"
                )
            else:
                state_answer: str | None = None
                for turn in turns:
                    answer = turn.get("answer")
                    if answer is not None and str(answer).strip():
                        state_answer = str(answer)
                final_correct = exact_correct(meta, state_answer)
                label_source = "exact"

            state_answer = None
            state_correct: bool | None = None
            for index, turn in enumerate(turns):
                answer = turn.get("answer")
                if answer is not None and str(answer).strip():
                    state_answer = str(answer)
                if state_answer is not None:
                    state_correct = exact_correct(meta, state_answer)

                features = turn.get("features") or {}
                record = {
                    "source_kind": source_kind,
                    "source_file": str(path.relative_to(ROOT)),
                    "run_id": run_id,
                    "task_id": task_id,
                    "task_type": turn.get("task_type", meta.get("task_type")),
                    "model": turn.get("model", ""),
                    "rel": meta.get("_rel", task_id),
                    "check": check,
                    "reward": float(meta.get("reward") or 0.0),
                    "wave": int(turn.get("wave", 0) or 0),
                    "turn": int(turn.get("turn", 0) or 0),
                    "answer_kind": turn.get("answer_kind", "none"),
                    "answer": answer,
                    "answer_chars": len(str(answer or "")),
                    "final_answer": state_answer,
                    "final_correct": final_correct,
                    "final_label_source": label_source,
                    "state_correct": state_correct,
                    "next_turn": (
                        int(turns[index + 1].get("wave", 0) or 0)
                        if index + 1 < len(turns)
                        else 0
                    ),
                    "next_cost": (
                        int(turns[index + 1].get("output_tokens", 0) or 0)
                        + math.ceil(
                            int(turns[index + 1].get("input_tokens", 0) or 0)
                            / 10
                        )
                        if index + 1 < len(turns)
                        else 0
                    ),
                    "n_turns": len(turns),
                    "n_waves": max(
                        int(item.get("wave", 0) or 0) for item in turns
                    ),
                }
                for name in NUMERIC:
                    record[name] = numeric_value(features, name)
                for name in CATEGORICAL:
                    value = features.get(name, "none")
                    record[name] = (
                        str(value) if value not in (None, "") else "none"
                    )
                # Keep a few turn-level features that the shipped model does
                # not use but later waves may need.
                record["script_timed_out"] = float(
                    bool(features.get("script_timed_out"))
                )
                record["script_error_len"] = len(
                    str(features.get("script_error") or "")
                )
                record["cost"] = float(
                    int(turn.get("output_tokens", 0) or 0)
                    + math.ceil(int(turn.get("input_tokens", 0) or 0) / 10)
                )
                rows.append(record)

    frame = pd.DataFrame(rows)
    return frame


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=OUT_DIR / "results" / "turns.csv",
    )
    args = parser.parse_args(argv)
    frame = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.out, index=False)
    groups = frame.drop_duplicates(["run_id", "task_id"])
    print(f"turns: {len(frame)}; groups: {len(groups)}")
    print(
        groups.groupby("source_kind").agg(
            groups=("task_id", "size"),
            tasks=("task_id", "nunique"),
            labelled=("final_correct", lambda s: int(s.notna().sum())),
        ).to_string()
    )
    print(f"out: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
