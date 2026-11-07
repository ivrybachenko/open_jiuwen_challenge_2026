"""CLI: solve a task set with the harness and print a score/tokens/minutes report.

Examples::

    python -m evaluation.harness_task_set_checker \
        --task-set data/task_set/example.yaml
    python -m evaluation.harness_task_set_checker \
        --task-set data/task_set/minimal.yaml --budget 50000 --max-tasks 2
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from evaluation.common.datasets import (
    ensure_harness_info,
    new_run_id,
    record_task_set_score,
    resolve_harness_version,
)
from evaluation.common.paths import (
    default_out_dir,
    default_tasks_root,
    repo_root,
    resolve_path,
    resolve_task_set_path,
)
from evaluation.common.reporting import format_seconds, format_tokens, write_json
from evaluation.common.runner import HarnessConfig, missing_llm_env, resolve_python
from evaluation.common.tasks import load_task_set, resolve_task_set
from evaluation.harness_task_set_checker.checker import check_task_set

log = logging.getLogger("evaluation.task_set")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.harness_task_set_checker",
        description="Run the harness on a task set and evaluate every answer.",
    )
    parser.add_argument(
        "--task-set",
        required=True,
        help="Path to a data/task_set/*.yaml (or *.json) file.",
    )
    parser.add_argument("--tasks-root", type=Path, default=None)
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument(
        "--python",
        default=None,
        help="Interpreter for the harness and for re-running tests.",
    )
    parser.add_argument("--model", default=None)
    parser.add_argument("--budget", type=int, default=None)
    parser.add_argument("--max-iterations", type=int, default=None)
    parser.add_argument("--max-tasks", type=int, default=None)
    parser.add_argument("--timeout", type=float, default=3600.0)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--allow-test-edits", action="store_true")
    parser.add_argument("--keep", action="store_true")
    parser.add_argument(
        "--fail-on-unsolved",
        action="store_true",
        help="Exit with code 1 if at least one task is unsolved.",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=None,
        help="Exit with code 1 if the score is below this value.",
    )
    parser.add_argument(
        "--record",
        action="store_true",
        help="Append/update data/harness_task_set_score/harness_v_<version>.tsv.",
    )
    parser.add_argument(
        "--harness-version",
        default=None,
        help="Required with --record; must match harness/pyproject.toml.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Run identifier for --record (default: UTC timestamp).",
    )
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=str(args.log_level).upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    missing = missing_llm_env()
    if missing:
        print(
            "error: set LLM_API_KEY before running the harness, e.g. "
            'LLM_API_KEY="$NEURAL_DEEP_API_KEY"',
            file=sys.stderr,
        )
        return 2

    root = resolve_path(args.repo_root) or repo_root()
    tasks_root = resolve_path(args.tasks_root) or default_tasks_root()

    version = None
    run_id = args.run_id or new_run_id()
    if args.record and not args.harness_version:
        print(
            "error: --harness-version is required with --record",
            file=sys.stderr,
        )
        return 2
    if args.harness_version:
        try:
            version = resolve_harness_version(root, args.harness_version)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    try:
        spec_path = resolve_task_set_path(args.task_set)
        spec = load_task_set(spec_path)
        tasks = resolve_task_set(spec, tasks_root)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    config = HarnessConfig(
        repo_root=root,
        python=args.python,
        model=args.model,
        budget=args.budget,
        max_iterations=args.max_iterations,
        timeout=args.timeout,
    )

    # Use the harness interpreter for re-running coding tests as well.
    test_python = args.python or resolve_python(config)

    try:
        report = check_task_set(
            spec,
            tasks,
            config,
            python=test_python,
            strict=args.strict,
            forbid_test_edits=not args.allow_test_edits,
            max_tasks=args.max_tasks,
            keep=args.keep,
        )
    except Exception as exc:  # noqa: BLE001 - CLI must print a useful error
        log.exception("task-set check failed")
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    out_path = args.out or default_out_dir() / f"{spec.name}.json"
    write_json(out_path, report.to_dict())

    if args.record:
        try:
            score_path = record_task_set_score(
                root,
                task_set_id=spec.name,
                harness_version=version,  # type: ignore[arg-type]
                run_id=run_id,
                score=report.summary.score,
                cost_tokens=report.summary.cost,
                cost_seconds=report.harness_duration_seconds,
            )
            info_path = ensure_harness_info(root, harness_version=version)
            print(f"recorded: {score_path}")
            print(f"run_id: {run_id}")
            print(f"harness info: {info_path}")
        except (OSError, ValueError) as exc:
            print(f"error: cannot record score: {exc}", file=sys.stderr)
            return 2

    summary = report.summary
    print(f"task set: {spec.name} (random_seed={spec.random_seed})")
    print(
        f"score: {summary.score:g} / {summary.max_score:g} "
        f"({summary.solved_tasks}/{summary.total_tasks} solved)"
    )
    print(
        "tokens: "
        + format_tokens(summary.input_tokens, summary.output_tokens, summary.cost)
    )
    print(f"time: {format_seconds(report.harness_duration_seconds)}")
    for outcome in report.outcomes:
        status = "SOLVED  " if outcome.verdict.solved else "UNSOLVED"
        print(
            f"  {status} {outcome.task.task_id:<24} "
            f"reward={outcome.task.reward:g} cost={outcome.cost} "
            f"check={outcome.task.check}"
        )
    print(f"report: {out_path}")
    if report.work_dir:
        print(f"work dir: {report.work_dir}")

    if args.min_score is not None and summary.score < args.min_score:
        return 1
    if args.fail_on_unsolved and summary.solved_tasks < summary.total_tasks:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
