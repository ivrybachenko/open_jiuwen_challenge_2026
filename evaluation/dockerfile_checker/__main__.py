"""CLI: build the image, check its size and run a small task set inside it.

Examples::

    python -m evaluation.dockerfile_checker
    python -m evaluation.dockerfile_checker --skip-build --image hack:latest
    python -m evaluation.dockerfile_checker --task-set data/task_set/minimal.yaml
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
from evaluation.common.reporting import (
    format_seconds,
    format_size,
    format_tokens,
    tail,
    write_json,
)
from evaluation.dockerfile_checker.checker import (
    DEFAULT_BUILD_TIMEOUT,
    DEFAULT_MAX_IMAGE_BYTES,
    DEFAULT_MAX_REPO_BYTES,
    DEFAULT_RUN_TIMEOUT,
    check_dockerfile,
)

log = logging.getLogger("evaluation.docker")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.dockerfile_checker",
        description="Check the Docker image size, build time and a minimal run.",
    )
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--image", default="hack:latest")
    parser.add_argument(
        "--task-set",
        default="minimal.yaml",
        help="Task-set file (default: minimal.yaml from data/task_set).",
    )
    parser.add_argument("--tasks-root", type=Path, default=None)
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--skip-run", action="store_true")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument(
        "--network",
        default=None,
        help="Docker network (the jury uses hack-net; the default bridge is used when omitted).",
    )
    parser.add_argument(
        "--cpus",
        default="8",
        help="Docker --cpus value (jury uses 8; lower it if the local engine has fewer CPUs).",
    )
    parser.add_argument(
        "--python",
        default=None,
        help="Interpreter used on the host to run unittest checks.",
    )
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--allow-test-edits", action="store_true")
    parser.add_argument("--max-image-gb", type=float, default=4.0)
    parser.add_argument("--max-repo-mb", type=float, default=100.0)
    parser.add_argument("--build-timeout", type=float, default=DEFAULT_BUILD_TIMEOUT)
    parser.add_argument("--run-timeout", type=float, default=DEFAULT_RUN_TIMEOUT)
    parser.add_argument("--model", default=None)
    parser.add_argument("--budget", type=int, default=None)
    parser.add_argument("--max-iterations", type=int, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=None,
        help="Directory for the task copies and solutions.json (must be visible to Docker).",
    )
    parser.add_argument("--keep", action="store_true")
    parser.add_argument("--fail-on-unsolved", action="store_true")
    parser.add_argument("--min-score", type=float, default=None)
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
        task_set_path = resolve_task_set_path(args.task_set)
        report = check_dockerfile(
            repo=root,
            image=args.image,
            task_set_path=task_set_path,
            tasks_root=tasks_root,
            build=not args.skip_build,
            skip_run=args.skip_run,
            no_cache=args.no_cache,
            network=args.network,
            cpus=args.cpus,
            python=args.python,
            strict=args.strict,
            forbid_test_edits=not args.allow_test_edits,
            max_image_bytes=int(args.max_image_gb * 1_000_000_000),
            max_repo_bytes=int(args.max_repo_mb * 1_000_000),
            build_timeout=args.build_timeout,
            run_timeout=args.run_timeout,
            model=args.model,
            budget=args.budget,
            max_iterations=args.max_iterations,
            work_dir=args.work_dir,
            keep=args.keep,
        )
    except Exception as exc:  # noqa: BLE001 - CLI must print a useful error
        log.exception("docker check failed")
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    out_path = args.out or default_out_dir() / "dockerfile_check.json"
    write_json(out_path, report.to_dict())

    if args.record and report.summary is not None and report.task_set:
        try:
            run_seconds = report.run.duration_seconds if report.run else 0.0
            score_path = record_task_set_score(
                root,
                task_set_id=report.task_set,
                harness_version=version,  # type: ignore[arg-type]
                run_id=run_id,
                score=report.summary.score,
                cost_tokens=report.summary.cost,
                cost_seconds=run_seconds,
            )
            info_path = ensure_harness_info(root, harness_version=version)
            print(f"recorded: {score_path}")
            print(f"run_id: {run_id}")
            print(f"harness info: {info_path}")
        except (OSError, ValueError) as exc:
            print(f"error: cannot record score: {exc}", file=sys.stderr)
            return 2

    print(f"image: {report.image}")
    if report.build is not None:
        status = "OK" if report.build.ok else "FAILED"
        print(
            f"build: {status} in {format_seconds(report.build.duration_seconds)} "
            f"(limit {format_seconds(args.build_timeout)})"
        )
        if not report.build.ok:
            print(tail(report.build.stderr, 4000))
    print(
        f"image size: {format_size(report.image_size_bytes)} "
        f"/ {format_size(report.max_image_bytes)} "
        f"{'OK' if report.image_size_ok else 'TOO LARGE'}"
    )
    print(
        f"repo size: {format_size(report.repo_size_bytes)} "
        f"/ {format_size(report.max_repo_bytes)} "
        f"{'OK' if report.repo_size_ok else 'TOO LARGE'}"
    )

    if report.run is not None:
        status = "OK" if report.run.ok else "FAILED"
        print(f"run: {status} in {format_seconds(report.run.duration_seconds)}")
        if not report.run.ok:
            print(tail(report.run.stderr, 4000))
    if report.summary is not None:
        summary = report.summary
        print(
            f"score: {summary.score:g} / {summary.max_score:g} "
            f"({summary.solved_tasks}/{summary.total_tasks} solved)"
        )
        print(
            "tokens: "
            + format_tokens(summary.input_tokens, summary.output_tokens, summary.cost)
        )
        for outcome in report.outcomes:
            status = "SOLVED  " if outcome.verdict.solved else "UNSOLVED"
            print(
                f"  {status} {outcome.task.task_id:<24} "
                f"reward={outcome.task.reward:g} cost={outcome.cost}"
            )

    print(f"report: {out_path}")
    if report.work_dir:
        print(f"work dir: {report.work_dir}")

    if report.build is not None and not report.build.ok:
        return 1
    if not report.image_size_ok or not report.repo_size_ok:
        return 1
    if report.run is not None and not report.run.ok:
        return 1
    if report.summary is not None:
        if args.min_score is not None and report.summary.score < args.min_score:
            return 1
        if (
            args.fail_on_unsolved
            and report.summary.solved_tasks < report.summary.total_tasks
        ):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
