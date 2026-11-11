"""CLI: solve one task with the harness and print a solved/tokens/minutes report.

Examples::

    python -m evaluation.harness_task_checker --task coding/solvable/0001
    python -m evaluation.harness_task_checker \
        --task data/task/coding/solvable/0001 --budget 50000 --model qwen3.6-35b-a3b
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from evaluation.common.datasets import (
    ensure_harness_info,
    new_run_id,
    record_task_score,
    resolve_harness_version,
)
from evaluation.common.paths import (
    default_out_dir,
    default_tasks_root,
    repo_root,
    resolve_path,
)
from evaluation.common.reporting import (
    format_seconds,
    format_tokens,
    write_json,
)
from evaluation.common.runner import HarnessConfig, missing_llm_env, resolve_python
from evaluation.common.tasks import load_task, resolve_task_dir, task_dataset_id
from evaluation.harness_task_checker.checker import check_task

log = logging.getLogger("evaluation.task")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.harness_task_checker",
        description="Run the harness on one task and evaluate the answer.",
    )
    parser.add_argument(
        "--task",
        required=True,
        help="Task directory, path relative to --tasks-root, or task_id.",
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
    parser.add_argument("--timeout", type=float, default=3600.0)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict answer comparison (no lenient integer/string cleanup).",
    )
    parser.add_argument(
        "--allow-test-edits",
        action="store_true",
        help="Do not fail coding tasks when test*.py files were edited.",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Keep the temporary task copy and harness output.",
    )
    parser.add_argument(
        "--record",
        action="store_true",
        help="Append/update data/harness_task_score/harness_v_<version>.tsv.",
    )
    parser.add_argument(
        "--harness-version",
        default=None,
        help="Required with --record; must match harness/pyproject.toml.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Run identifier for --record (default: a random UUID).",
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
        task = load_task(resolve_task_dir(args.task, tasks_root))
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    dataset_id = task_dataset_id(task, tasks_root)

    config = HarnessConfig(
        repo_root=root,
        python=args.python,
        model=args.model,
        budget=args.budget,
        max_iterations=args.max_iterations,
        timeout=args.timeout,
    )

    # Use the same interpreter for the harness and for re-running the tests:
    # the harness venv may contain task dependencies that the system Python
    # does not have.
    test_python = args.python or resolve_python(config)

    try:
        report = check_task(
            task,
            config,
            python=test_python,
            strict=args.strict,
            forbid_test_edits=not args.allow_test_edits,
            keep=args.keep,
        )
    except Exception as exc:  # noqa: BLE001 - CLI must print a useful error
        log.exception("task check failed")
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    out_path = args.out or default_out_dir() / f"{task.task_id}.json"
    write_json(out_path, report.to_dict())

    if args.record:
        try:
            score_path = record_task_score(
                root,
                task_id=dataset_id,
                harness_version=version,  # type: ignore[arg-type]
                run_id=run_id,
                is_solved_correctly=report.outcome.verdict.solved,
                cost_tokens=report.outcome.cost,
                cost_seconds=report.harness_duration_seconds,
            )
            info_path = ensure_harness_info(root, harness_version=version)
            print(f"recorded: {score_path}")
            print(f"run_id: {run_id}")
            print(f"harness info: {info_path}")
        except (OSError, ValueError) as exc:
            print(f"error: cannot record score: {exc}", file=sys.stderr)
            return 2

    print(
        f"{dataset_id} ({task.task_id}) [{task.task_type}] check={task.check} "
        f"reward={task.reward:g}"
    )
    print(
        f"verdict: {'SOLVED' if report.solved else 'UNSOLVED'} - "
        f"{report.outcome.verdict.detail}"
    )
    print(
        "tokens: "
        + format_tokens(
            report.outcome.input_tokens,
            report.outcome.output_tokens,
            report.outcome.cost,
        )
    )
    print(f"time: {format_seconds(report.harness_duration_seconds)}")
    print(f"report: {out_path}")
    if report.work_dir:
        print(f"work dir: {report.work_dir}")

    return 0 if report.solved else 1


if __name__ == "__main__":
    raise SystemExit(main())
