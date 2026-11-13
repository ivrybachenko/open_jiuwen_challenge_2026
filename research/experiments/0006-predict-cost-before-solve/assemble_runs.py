#!/usr/bin/env python3
"""Assemble a ``current_runs.csv`` from a partial collection run.

The full collector writes the CSV only after all repeats.  When a repeat is
complete but later repeats are not, this script extracts one repeat from the
work directory, using the evaluator correctness files and the attempt logs.

Usage::

    harness/.venv/bin/python \
        research/experiments/0006-predict-cost-before-solve/assemble_runs.py \
        --work-root /tmp/pred0006 --rep 100 \
        --out research/experiments/0006-predict-cost-before-solve/results/current_runs.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]


def _id_to_rel() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for tj in (ROOT / "data" / "task").glob("*/*/*/task.json"):
        try:
            meta = json.loads(tj.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        mapping[meta.get("task_id", "")] = "/".join(tj.parts[-4:-1])
    return mapping


def _turn_costs(path: Path) -> dict[tuple[str, str], list[int]]:
    by_turn: dict[tuple[str, str], list[tuple[int, int]]] = {}
    if not path.is_file():
        return {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        cost = int(record["output_tokens"]) + math.ceil(
            int(record["input_tokens"]) / 10)
        key = (record["run_id"], record["task_id"])
        by_turn.setdefault(key, []).append((int(record["wave"]), cost))
    return {key: [cost for _, cost in sorted(values)]
            for key, values in by_turn.items()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, default=Path("/tmp/pred0006"))
    parser.add_argument("--rep", type=int, default=100)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    id_to_rel = _id_to_rel()
    rows: list[dict[str, Any]] = []
    rep_dir = args.work_root / f"rep{args.rep}"
    for shard in sorted(rep_dir.glob("shard*")):
        solutions_file = shard / "solutions.json"
        if not solutions_file.is_file():
            continue
        solutions = json.loads(solutions_file.read_text(encoding="utf-8"))
        correctness_file = shard / "correctness.json"
        correctness = (json.loads(correctness_file.read_text(encoding="utf-8"))
                       if correctness_file.is_file() else {})
        costs = _turn_costs(shard / "work" / "traj" / "bash_attempts.jsonl")
        run_id = f"pred0006-r{args.rep}-s{shard.name.replace('shard', '')}"
        for task_id, payload in solutions.get("solutions", {}).items():
            turns = costs.get((run_id, task_id), [])
            attempts = int(payload.get("attempts", len(turns) or 1))
            rows.append({
                "rep": 1,
                "shard": shard.name,
                "task_id": task_id,
                "rel": id_to_rel.get(task_id, task_id),
                "cost": int(payload.get("cost", 0)),
                "wave1_cost": turns[0] if turns else None,
                "wave2_cost": sum(turns[1:]) if len(turns) > 1 else 0,
                "turns": attempts,
                "answered_wave1": int(attempts == 1),
                "solved_flag": bool(payload.get("solved", False)),
                "correct": bool(correctness.get(task_id, False)),
                "note": payload.get("note", ""),
            })
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
