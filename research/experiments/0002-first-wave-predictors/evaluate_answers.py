#!/usr/bin/env python3
"""Evaluate answers produced by the data-collection harness run.

The harness only records whether an answer was submitted, not whether it is
correct.  This script runs the repository answer evaluator on the task copies
that the harness used and writes a ``task_id -> bool`` map for the trainer.

Usage::

    python research/experiments/0002-first-wave-predictors/evaluate_answers.py \
        --tasks-dirs /tmp/exp0002_shards/shard0 \
                     /tmp/exp0002_shards/shard1 \
                     /tmp/exp0002_shards/shard2 \
        --out research/experiments/0002-first-wave-predictors/results/correctness.json
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.answer_evaluator.evaluator import evaluate_task  # noqa: E402
from evaluation.common.tasks import load_task  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-dirs", nargs="+", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args(argv)

    results: dict[str, bool] = {}
    details: dict[str, dict[str, object]] = {}
    for tasks_dir in args.tasks_dirs:
        for child in sorted(tasks_dir.iterdir()):
            if not (child / "task.json").is_file():
                continue
            try:
                task = load_task(child)
                verdict = evaluate_task(task, timeout=args.timeout)
                results[task.task_id] = bool(verdict.solved)
                details[task.task_id] = verdict.to_dict()
            except Exception as exc:  # noqa: BLE001 - one task must not stop the batch
                results[child.name] = False
                details[child.name] = {
                    "error": f"{type(exc).__name__}: {exc}",
                    "traceback": traceback.format_exc()[-2000:],
                }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    details_path = args.out.with_name(args.out.stem + "_details.json")
    details_path.write_text(
        json.dumps(details, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    solved = sum(results.values())
    print(f"evaluated {len(results)} tasks: solved={solved}, failed={len(results)-solved}")
    print(f"wrote {args.out}")
    print(f"wrote {details_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
