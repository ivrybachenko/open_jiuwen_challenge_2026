"""CLI: measure the repository size and compare it with the 100 MB limit.

Examples::

    python -m evaluation.repo_size_checker
    python -m evaluation.repo_size_checker --metric without-git
    python -m evaluation.repo_size_checker --max-mb 50 --verbose
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from evaluation.common.paths import default_out_dir, repo_root, resolve_path
from evaluation.common.reporting import format_size, write_json
from evaluation.repo_size_checker.checker import (
    DEFAULT_MAX_REPO_BYTES,
    METRICS,
    LOCAL_ONLY_DIRS,
    check_repo_size,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.repo_size_checker",
        description="Measure the repository size and check it against the limit.",
    )
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument(
        "--max-mb",
        type=float,
        default=DEFAULT_MAX_REPO_BYTES / 1_000_000,
        help="Limit in decimal megabytes (default: 100, the competition limit).",
    )
    parser.add_argument(
        "--metric",
        choices=METRICS,
        default="tracked",
        help=(
            "What to compare with the limit: files tracked by git (default, "
            "what the jury clones), the working tree without .git, or everything."
        ),
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="How many root entries to show in the breakdown (0 for all).",
    )
    parser.add_argument(
        "--largest",
        type=int,
        default=5,
        help="How many largest files to show (0 to hide).",
    )
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print the measured size and the verdict.",
    )
    return parser.parse_args(argv)


def _print_breakdown(report, top: int) -> None:
    entries = report.top_level
    if top > 0:
        entries = entries[:top]
    if not entries:
        return
    print("breakdown by root entry:")
    width = max(len(entry.name) for entry in entries)
    for entry in entries:
        line = (
            f"  {entry.name:<{width}}  {format_size(entry.bytes):>10}"
            f"  ({entry.files} files"
        )
        if report.tracked_bytes is not None:
            if entry.name in LOCAL_ONLY_DIRS and entry.untracked_bytes > 0:
                line += f", untracked {format_size(entry.untracked_bytes)}"
            else:
                line += f", tracked {format_size(entry.tracked_bytes)}"
        print(line + ")")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    root = resolve_path(args.repo_root) or repo_root()
    try:
        report = check_repo_size(
            repo=root,
            max_bytes=int(args.max_mb * 1_000_000),
            metric=args.metric,
            top_n=max(0, args.top),
            largest_n=max(0, args.largest),
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    out_path = args.out or default_out_dir() / "repo_size_check.json"
    try:
        write_json(out_path, report.to_dict())
    except OSError as exc:
        print(f"error: cannot write report: {exc}", file=sys.stderr)
        return 2

    verdict = "OK" if report.ok else "TOO LARGE"
    print(
        f"repo: {report.repo}\n"
        f"size: {format_size(report.measured_bytes)} / "
        f"{format_size(report.max_bytes)} {verdict} "
        f"({report.measured_source})"
    )
    if not args.quiet:
        print(f"  total with .git: {format_size(report.total_bytes)}")
        print(f"  .git: {format_size(report.git_bytes)}")
        print(f"  working tree without .git: {format_size(report.without_git_bytes)}")
        if report.tracked_bytes is not None:
            print(
                f"  tracked by git: {format_size(report.tracked_bytes)} "
                f"in {report.tracked_files} files"
            )
            if report.untracked_bytes:
                print(
                    "  not in git: "
                    f"{format_size(report.untracked_bytes)} "
                    "(kept locally, not part of the clone)"
                )
        _print_breakdown(report, max(0, args.top))
        if report.largest_files:
            print("largest files:")
            for entry in report.largest_files:
                print(f"  {format_size(entry.bytes):>10}  {entry.path}")
        print(f"report: {out_path}")

    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
