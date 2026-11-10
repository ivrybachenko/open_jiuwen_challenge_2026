"""CLI: evaluate the answer of one already-solved task.

Examples::

    python -m evaluation.answer_evaluator --task data/task/coding/solvable/0001
    python -m evaluation.answer_evaluator --task coding/solvable/0001 --answer path/to/answer.txt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from evaluation.answer_evaluator.evaluator import evaluate_task
from evaluation.common.paths import default_tasks_root
from evaluation.common.reporting import write_json
from evaluation.common.tasks import load_task, resolve_task_dir


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.answer_evaluator",
        description="Evaluate one task answer without running the harness.",
    )
    parser.add_argument(
        "--task",
        required=True,
        help="Task directory, path relative to --tasks-root, or task_id.",
    )
    parser.add_argument("--tasks-root", type=Path, default=None)
    parser.add_argument(
        "--answer",
        type=Path,
        default=None,
        help="Read the answer from this file instead of answer.txt.",
    )
    parser.add_argument(
        "--python",
        default=None,
        help="Interpreter used to run unittest checks (default: current).",
    )
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Disable lenient integer extraction and case-insensitive strings.",
    )
    parser.add_argument("--out", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    tasks_root = args.tasks_root or default_tasks_root()
    try:
        task = load_task(resolve_task_dir(args.task, tasks_root))
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    answer = None
    if args.answer is not None:
        try:
            answer = args.answer.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot read {args.answer}: {exc}", file=sys.stderr)
            return 2

    verdict = evaluate_task(
        task,
        answer=answer,
        python=args.python,
        timeout=args.timeout,
        strict=args.strict,
    )
    payload = verdict.to_dict()
    if args.out is not None:
        write_json(args.out, payload)
        print(f"report: {args.out}")

    print(
        f"{task.task_id} [{task.task_type}] check={verdict.check} "
        f"reward={task.reward:g} solved={'yes' if verdict.solved else 'no'}"
    )
    print(f"detail: {verdict.detail}")
    return 0 if verdict.solved else 1


if __name__ == "__main__":
    raise SystemExit(main())
