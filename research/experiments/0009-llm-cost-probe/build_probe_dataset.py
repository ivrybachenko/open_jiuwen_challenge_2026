#!/usr/bin/env python3
"""Collect one wave-1 overview per task for the LLM probe experiment.

The overview is exactly what the harness sends before the first model call, so
it is a legitimate pre-solve input.  One repeat per task is enough: the overview
is deterministic and does not depend on the model.

Usage::

    harness/.venv/bin/python \
        research/experiments/0009-llm-cost-probe/build_probe_dataset.py \
        --fresh-root /tmp/pred0006 \
        --out research/experiments/0009-llm-cost-probe/results/probe_tasks.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _id_to_meta() -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    for tj in (ROOT / "data" / "task").glob("*/*/*/task.json"):
        try:
            meta = json.loads(tj.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        mapping[meta.get("task_id", "")] = {
            "rel": "/".join(tj.parts[-4:-1]),
            "task_type": meta.get("task_type", tj.parts[-4]),
            "instruction": meta.get("instruction", ""),
            "reward": str(meta.get("reward", "")),
        }
    return mapping


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fresh-root", type=Path, default=Path("/tmp/pred0006"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    meta = _id_to_meta()
    seen: dict[str, dict[str, str]] = {}
    paths = sorted(args.fresh_root.glob("rep*/shard*/work/traj/bash_attempts.jsonl"))
    if not paths:
        paths = sorted((ROOT / "data" / "trajectories").glob(
            "exp0002-shard*/bash_attempts.jsonl"))
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if int(record.get("wave", 0)) != 1:
                continue
            task_id = record["task_id"]
            if task_id in seen:
                continue
            info = meta.get(task_id, {})
            seen[task_id] = {
                "task_id": task_id,
                "rel": info.get("rel", task_id),
                "task_type": info.get("task_type", record.get("task_type", "")),
                "instruction": info.get("instruction", ""),
                "reward": info.get("reward", ""),
                "overview": record.get("overview", ""),
            }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for row in seen.values():
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(seen)} tasks to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
