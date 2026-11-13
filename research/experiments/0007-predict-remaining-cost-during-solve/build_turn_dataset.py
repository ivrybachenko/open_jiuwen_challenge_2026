#!/usr/bin/env python3
"""Build turn-level datasets from harness attempt logs.

The script joins three sources:

* attempt records (``bash_attempts.jsonl``) with per-turn model and script data;
* evaluator correctness from ``tasks.jsonl`` or ``correctness.json``;
* task metadata (category, solvable/impossible path label).

It writes two CSVs:

* ``turn_groups.csv`` -- one row per (run, task) after the first turn, with
  the remaining/total cost and correctness targets;
* ``turn_pairs.csv`` -- one row per first->second turn pair, for next-turn
  cost prediction.

Usage::

    harness/.venv/bin/python \
        research/experiments/0007-predict-remaining-cost-during-solve/build_turn_dataset.py \
        --fresh-root /tmp/pred0006 \
        --out-dir research/experiments/0007-predict-remaining-cost-during-solve/results
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]

SCRIPT_PATTERNS = {
    "n_cat": r"\bcat\b",
    "n_grep": r"\bgrep\b",
    "n_find": r"\bfind\b",
    "n_ls": r"\bls\b",
    "n_head": r"\bhead\b",
    "n_tail": r"\btail\b",
    "n_awk": r"\bawk\b",
    "n_sed": r"\bsed\b",
    "n_sort": r"\bsort\b",
    "n_wc": r"\bwc\b",
    "n_python": r"\bpython3?\b",
    "n_test": r"\b(pytest|unittest|test_)\b",
    "n_for": r"\bfor\b",
    "n_while": r"\bwhile\b",
    "n_if": r"\bif\b",
    "n_pipe": r"\|",
    "n_semicolon": r";",
    "n_redirect": r">",
    "n_echo": r"\becho\b",
    "n_impossible": r"(?i)\bimpossible\b",
}
SCRIPT_RE = {name: re.compile(pattern) for name, pattern in SCRIPT_PATTERNS.items()}


def _id_to_rel() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for tj in (ROOT / "data" / "task").glob("*/*/*/task.json"):
        try:
            meta = json.loads(tj.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        mapping[meta.get("task_id", "")] = "/".join(tj.parts[-4:-1])
    return mapping


def _cost(record: dict[str, Any]) -> int:
    return int(record["output_tokens"]) + math.ceil(int(record["input_tokens"]) / 10)


def _script_features(script: str) -> dict[str, int]:
    feats = {
        "script_chars": len(script or ""),
        "script_lines": (script or "").count("\n") + (1 if script else 0),
        "script_words": len((script or "").split()),
    }
    for name, pattern in SCRIPT_RE.items():
        feats[name] = len(pattern.findall(script or ""))
    return feats


def _turn_features(record: dict[str, Any]) -> dict[str, Any]:
    features = record.get("features") or {}
    script = record.get("script") or ""
    output = record.get("output") or ""
    overview = record.get("overview") or ""
    answer = record.get("answer") or ""
    row: dict[str, Any] = {
        "task_id": record["task_id"],
        "task_type": record.get("task_type", ""),
        "model": record.get("model", ""),
        "wave": int(record.get("wave", 0)),
        "turn": int(record.get("turn", 0)),
        "input_tokens": int(record.get("input_tokens", 0)),
        "output_tokens": int(record.get("output_tokens", 0)),
        "cost": _cost(record),
        "reasoning_chars": len(record.get("reasoning") or ""),
        "reasoning_words": len((record.get("reasoning") or "").split()),
        "output_chars": len(output),
        "output_lines": output.count("\n") + (1 if output else 0),
        "exit_code": record.get("exit_code"),
        "timed_out": int(bool(record.get("timed_out"))),
        "script_error": len(record.get("script_error") or ""),
        "hit_token_limit": int(bool(features.get("hit_token_limit"))),
        "finish_reason": record.get("finish_reason", ""),
        "answer_kind": record.get("answer_kind", "none"),
        "answer_chars": len(answer),
        "overview_chars": len(overview),
        "overview_lines": overview.count("\n") + (1 if overview else 0),
        "overview_fails": len(re.findall(r"\b(?:FAIL|FAILED|ERROR|Traceback)\b", overview)),
        "overview_passes": len(re.findall(r"\b(?:PASS|PASSED|OK|passed)\b", overview)),
        "overview_notimplemented": overview.count("NotImplementedError"),
        "overview_asserts": overview.count("AssertionError"),
        "overview_syntax": overview.count("SyntaxError"),
        "overview_typeerror": overview.count("TypeError"),
        "overview_filenames": len(set(re.findall(
            r"\b[\w.-]+\.(?:csv|tsv|json|jsonl|txt|md|py|log|yaml|yml)\b",
            overview))),
        "overview_dollar_lines": overview.count("$ "),
        "tests_in_overview": int(bool(features.get("tests_in_overview"))),
        "reward": float(features.get("reward", 0.0)),
        "reasoning_keyword_impossible": int(
            features.get("reasoning_keyword_impossible", 0)
        ),
        "reasoning_keyword_give_up": int(features.get("reasoning_keyword_give_up", 0)),
        "script_has_python": int(bool(features.get("script_has_python"))),
        "script_has_tests": int(bool(features.get("script_has_tests"))),
        "script_has_file_ops": int(bool(features.get("script_has_file_ops"))),
        "script_has_write_answer": int(bool(features.get("script_has_write_answer"))),
        "script_mentions_impossible": int(
            bool(features.get("script_mentions_impossible"))
        ),
    }
    row.update(_script_features(script))
    row["answer_present"] = int(row["answer_kind"] in {"done", "value"})
    row["answer_impossible"] = int(row["answer_kind"] == "impossible")
    row["exit_bad"] = int(row["exit_code"] not in (0, None))
    return row


def _load_records(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def _load_run_correctness(run_dir: Path) -> dict[str, bool]:
    """Read evaluator verdicts from a run's tasks.jsonl."""
    result: dict[str, bool] = {}
    tasks_file = run_dir / "tasks.jsonl"
    if not tasks_file.is_file():
        return result
    for line in tasks_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        verdict = row.get("verdict") or {}
        if "solved" in verdict:
            result[row["task_id"]] = bool(verdict["solved"])
        elif "solved" in row:
            result[row["task_id"]] = bool(row["solved"])
    return result


def _iter_trajectories(
    fresh_root: Path | None,
    fresh_pattern: str = "rep*/shard*/work/traj/bash_attempts.jsonl",
) -> list[tuple[Path, str, dict[str, bool]]]:
    """(attempts path, source tag, correctness map)."""
    sources: list[tuple[Path, str, dict[str, bool]]] = []
    # exp0002: one wave per task; correctness lives in the experiment results.
    exp0002_correctness: dict[str, bool] = {}
    correctness_file = (
        ROOT / "research" / "experiments" / "0002-first-wave-predictors"
        / "results" / "correctness.json"
    )
    if correctness_file.is_file():
        exp0002_correctness = json.loads(
            correctness_file.read_text(encoding="utf-8")
        )
    for path in sorted((ROOT / "data" / "trajectories").glob(
            "exp0002-shard*/bash_attempts.jsonl")):
        sources.append((path, "exp0002", exp0002_correctness))
    # Existing research runs: <run>/traj/bash_attempts.jsonl + <run>/tasks.jsonl
    for path in sorted((ROOT / "research" / "experiments").rglob("bash_attempts.jsonl")):
        if path.parent.name != "traj":
            continue
        run_dir = path.parent.parent
        correctness = _load_run_correctness(run_dir)
        sources.append((path, f"exp:{run_dir.relative_to(ROOT)}", correctness))
    # Fresh 0006 runs: <root>/repN/shardK/work/traj/bash_attempts.jsonl,
    # correctness in the same shard directory.
    if fresh_root and fresh_root.exists():
        for path in sorted(fresh_root.glob(fresh_pattern)):
            shard_dir = path.parent.parent.parent
            correctness_file = shard_dir / "correctness.json"
            correctness = {}
            if correctness_file.is_file():
                correctness = json.loads(correctness_file.read_text(encoding="utf-8"))
            sources.append((path, f"fresh:{shard_dir.relative_to(fresh_root)}", correctness))
    return sources


def build(
    fresh_root: Path | None,
    fresh_pattern: str = "rep*/shard*/work/traj/bash_attempts.jsonl",
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    id_to_rel = _id_to_rel()
    groups: list[dict[str, Any]] = []
    pairs: list[dict[str, Any]] = []
    for path, source, correctness in _iter_trajectories(fresh_root, fresh_pattern):
        by_group: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for record in _load_records(path):
            if record.get("model") != "qwen3.6-35b-a3b-noreason":
                continue
            key = (record.get("run_id", ""), record["task_id"])
            by_group.setdefault(key, []).append(record)
        for (run_id, task_id), records in by_group.items():
            records.sort(key=lambda r: (int(r.get("turn", 0)), int(r.get("wave", 0))))
            first = records[0]
            first_row = _turn_features(first)
            total_cost = sum(_cost(r) for r in records)
            remaining_cost = total_cost - first_row["cost"]
            row = dict(first_row)
            row.update({
                "run_id": run_id,
                "source": source,
                "rel": id_to_rel.get(task_id, task_id),
                "impossible_label": int("impossible" in id_to_rel.get(task_id, "")),
                "n_turns": len(records),
                "total_cost": total_cost,
                "remaining_cost": remaining_cost,
                "answered": int(first_row["answer_kind"] in {"done", "value"}),
                "has_correctness": int(task_id in correctness),
                "correct": int(bool(correctness.get(task_id, False))),
                "correct_after_more": int(bool(correctness.get(task_id, False))),
            })
            groups.append(row)
            if len(records) > 1:
                second = records[1]
                pair = {
                    "run_id": run_id,
                    "source": source,
                    "task_id": task_id,
                    "rel": id_to_rel.get(task_id, task_id),
                    "task_type": first_row["task_type"],
                    "prev_input": first_row["input_tokens"],
                    "prev_output": first_row["output_tokens"],
                    "prev_cost": first_row["cost"],
                    "exec_chars": first_row["output_chars"],
                    "exec_lines": first_row["output_lines"],
                    "script_chars": first_row["script_chars"],
                    "hit_token_limit": first_row["hit_token_limit"],
                    "answer_kind": first_row["answer_kind"],
                    "prev_exit_bad": first_row["exit_bad"],
                    "next_input": second["input_tokens"],
                    "next_output": second["output_tokens"],
                    "next_cost": _cost(second),
                    "next_answer_kind": second.get("answer_kind", "none"),
                }
                pairs.append(pair)
    return groups, pairs


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fresh-root", type=Path, default=Path("/tmp/pred0006"))
    parser.add_argument("--out-dir", type=Path,
                        default=Path(__file__).resolve().parent / "results")
    parser.add_argument("--fresh-pattern", default="rep100/shard*/work/traj/bash_attempts.jsonl")
    args = parser.parse_args(argv)
    groups, pairs = build(args.fresh_root, args.fresh_pattern)
    _write_csv(groups, args.out_dir / "turn_groups.csv")
    _write_csv(pairs, args.out_dir / "turn_pairs.csv")
    print(f"groups: {len(groups)}; pairs: {len(pairs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
