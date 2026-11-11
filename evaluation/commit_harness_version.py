"""Commit (benchmark) one harness version into the score datasets.

Usage::

    LLM_API_KEY="$NEURAL_DEEP_API_KEY" \
    python -m evaluation.commit_harness_version --harness-version 0001

The script:
1. verifies that ``harness/pyproject.toml`` contains the requested version;
2. verifies that ``data/harness_info/harness_info.tsv`` has a row for it;
3. appends results to ``data/harness_task_score/harness_v_<version>.tsv`` and
   ``data/harness_task_set_score/harness_v_<version>.tsv`` (existing rows are
   kept);
4. runs the harness 5 times on every task and 5 times on the example task set;
5. records every row under its own unique ``run_id``.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from evaluation.common.datasets import (
    has_harness_info,
    new_run_id,
    record_task_score,
    record_task_set_score,
    resolve_harness_version,
)
from evaluation.common.paths import (
    default_tasks_root,
    repo_root,
    resolve_path,
    resolve_task_set_path,
)
from evaluation.common.reporting import format_seconds, format_tokens
from evaluation.common.runner import HarnessConfig, missing_llm_env, resolve_python
from evaluation.common.tasks import (
    EvaluationTask,
    load_task,
    load_task_set,
    resolve_task_set,
    task_dataset_id,
)
from evaluation.harness_task_checker.checker import check_task
from evaluation.harness_task_set_checker.checker import check_task_set

log = logging.getLogger("evaluation.commit")

DEFAULT_RUNS = 5
DEFAULT_MODEL = "qwen3.6-35b-a3b"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.commit_harness_version",
        description="Benchmark one harness version and fill the score datasets.",
    )
    parser.add_argument(
        "--harness-version",
        required=True,
        help="Version that must match harness/pyproject.toml.",
    )
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--python", default=None)
    parser.add_argument("--budget", type=int, default=None)
    parser.add_argument("--max-iterations", type=int, default=None)
    parser.add_argument("--timeout", type=float, default=3600.0)
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--tasks-root", type=Path, default=None)
    parser.add_argument("--task-set", default="example.yaml")
    parser.add_argument(
        "--tasks-from",
        default=None,
        help=(
            "Task-set file that selects the tasks for per-task runs. "
            "Default: every task under --tasks-root."
        ),
    )
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=None,
        help="Limit per-task repetitions (useful for a quick smoke test).",
    )
    parser.add_argument(
        "--skip-set",
        action="store_true",
        help="Do not run the task-set part (useful for a quick smoke test).",
    )
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--allow-test-edits", action="store_true")
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args(argv)


def load_all_tasks(tasks_root: Path) -> list[EvaluationTask]:
    tasks: list[EvaluationTask] = []
    for task_json in sorted(tasks_root.rglob("task.json")):
        tasks.append(load_task(task_json.parent))
    return tasks


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=str(args.log_level).upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    missing = missing_llm_env()
    if missing:
        print(
            "error: set LLM_API_KEY before running the benchmark, e.g. "
            'LLM_API_KEY="$NEURAL_DEEP_API_KEY"',
            file=sys.stderr,
        )
        return 2

    root = resolve_path(args.repo_root) or repo_root()
    tasks_root = resolve_path(args.tasks_root) or default_tasks_root()

    try:
        version = resolve_harness_version(root, args.harness_version)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not has_harness_info(root, version):
        print(
            f"error: data/harness_info/harness_info.tsv has no row for "
            f"harness_version={version!r}",
            file=sys.stderr,
        )
        return 2

    if args.runs < 1:
        print("error: --runs must be positive", file=sys.stderr)
        return 2

    selection_spec = None
    if args.tasks_from:
        try:
            selection_spec = load_task_set(resolve_task_set_path(args.tasks_from))
            selected = resolve_task_set(selection_spec, tasks_root)
        except (FileNotFoundError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        # A set may repeat a task; run it once per benchmark iteration.
        seen: set[Path] = set()
        tasks = []
        for task in selected:
            root_path = task.root.resolve()
            if root_path not in seen:
                seen.add(root_path)
                tasks.append(task)
    else:
        tasks = load_all_tasks(tasks_root)

    if args.max_tasks is not None:
        tasks = tasks[: args.max_tasks]
    if not tasks:
        print(f"error: no task.json found under {tasks_root}", file=sys.stderr)
        return 2

    spec = None
    set_tasks: list[EvaluationTask] = []
    if not args.skip_set:
        try:
            spec = load_task_set(resolve_task_set_path(args.task_set))
            set_tasks = resolve_task_set(spec, tasks_root)
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
    test_python = args.python or resolve_python(config)

    task_score_path = (
        root / "data" / "harness_task_score" / f"harness_v_{version}.tsv"
    )
    set_score_path = (
        root / "data" / "harness_task_set_score" / f"harness_v_{version}.tsv"
    )
    batch = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")

    print(f"harness_version: {version}")
    print(f"runs: {args.runs}")
    print(f"tasks: {len(tasks)}")
    if selection_spec is not None:
        print(f"tasks from: {selection_spec.name}")
    if spec is not None:
        print(f"task_set: {spec.name} ({len(set_tasks)} tasks)")
    print(f"task dataset: {task_score_path}")
    print(f"set dataset:  {set_score_path}")
    print(f"batch: {batch}")

    started = time.monotonic()
    for run_index in range(1, args.runs + 1):
        print(f"\n=== run {run_index}/{args.runs} ===")

        for index, task in enumerate(tasks, start=1):
            dataset_id = task_dataset_id(task, tasks_root)
            run_id = new_run_id()
            task_config = replace(config, run_id=run_id)
            try:
                report = check_task(
                    task,
                    task_config,
                    python=test_python,
                    strict=args.strict,
                    forbid_test_edits=not args.allow_test_edits,
                    keep=False,
                )
                solved = report.outcome.verdict.solved
                cost = report.outcome.cost
                seconds = report.harness_duration_seconds
                record_task_score(
                    root,
                    task_id=dataset_id,
                    harness_version=version,
                    run_id=run_id,
                    is_solved_correctly=solved,
                    cost_tokens=cost,
                    cost_seconds=seconds,
                )
                print(
                    f"  [{index}/{len(tasks)}] {dataset_id} "
                    f"solved={'yes' if solved else 'no'} "
                    f"cost={cost} time={format_seconds(seconds)}"
                )
            except Exception as exc:  # noqa: BLE001 - keep the benchmark going
                log.exception("task %s failed", dataset_id)
                record_task_score(
                    root,
                    task_id=dataset_id,
                    harness_version=version,
                    run_id=run_id,
                    is_solved_correctly=False,
                    cost_tokens=0,
                    cost_seconds=0.0,
                )
                print(
                    f"  [{index}/{len(tasks)}] {dataset_id} "
                    f"ERROR {type(exc).__name__}: {exc}"
                )

        if spec is not None:
            set_run_id = new_run_id()
            set_config = replace(config, run_id=set_run_id)
            try:
                report = check_task_set(
                    spec,
                    set_tasks,
                    set_config,
                    python=test_python,
                    strict=args.strict,
                    forbid_test_edits=not args.allow_test_edits,
                    keep=False,
                )
                record_task_set_score(
                    root,
                    task_set_id=spec.name,
                    harness_version=version,
                    run_id=set_run_id,
                    score=report.summary.score,
                    cost_tokens=report.summary.cost,
                    cost_seconds=report.harness_duration_seconds,
                )
                print(
                    f"  set {spec.name}: score={report.summary.score:g}/"
                    f"{report.summary.max_score:g} "
                    f"({report.summary.solved_tasks}/{report.summary.total_tasks}) "
                    "tokens: "
                    + format_tokens(
                        report.summary.input_tokens,
                        report.summary.output_tokens,
                        report.summary.cost,
                    )
                    + f" time={format_seconds(report.harness_duration_seconds)}"
                )
            except Exception as exc:  # noqa: BLE001 - keep the benchmark going
                log.exception("task set %s failed", spec.name)
                record_task_set_score(
                    root,
                    task_set_id=spec.name,
                    harness_version=version,
                    run_id=set_run_id,
                    score=0.0,
                    cost_tokens=0,
                    cost_seconds=0.0,
                )
                print(f"  set {spec.name}: ERROR {type(exc).__name__}: {exc}")

    elapsed = time.monotonic() - started
    print(f"\ndone in {format_seconds(elapsed)}")
    print(f"task dataset: {task_score_path}")
    print(f"set dataset:  {set_score_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
