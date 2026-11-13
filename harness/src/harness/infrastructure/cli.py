"""Command-line arguments for the harness.

This module only parses arguments.  ``harness.run_agent.main`` owns the
process entrypoint; wave scheduling and the task loop live in
:mod:`harness.solving.runner`.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="run_agent.py")
    parser.add_argument("--tasks-dir", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument(
        "--budget",
        type=int,
        default=None,
        help="output-token budget; BUDGET is used when absent, then 100000.",
    )
    parser.add_argument("--model", default=None)
    parser.add_argument("--wave2-model", default=None,
                        help="model for the second wave; defaults to --model")
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Deprecated; kept for evaluator compatibility and ignored.",
    )
    parser.add_argument("--agent-workspace", type=Path, default=None)
    parser.add_argument(
        "--trajectories-dir",
        type=Path,
        default=None,
        help=(
            "Directory for attempt features; TRAJECTORIES_DIR is used when the "
            "flag is absent."
        ),
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help=(
            "Opaque evaluation run identifier stored in each attempt record; "
            "HARNESS_RUN_ID is used when the flag is absent."
        ),
    )
    parser.add_argument("--max-tasks", type=int, default=None)
    parser.add_argument("--wave1-max-tokens", type=int, default=None)
    parser.add_argument("--wave2-max-tokens", type=int, default=None)
    parser.add_argument("--wave2-max-tasks", type=int, default=None)
    parser.add_argument(
        "--max-waves",
        type=int,
        default=None,
        help=(
            "Wave 1 plus follow-up waves; HARNESS_MAX_WAVES is used when the "
            "flag is absent, then 8."
        ),
    )
    parser.add_argument("--overview-max-tokens", type=int, default=None)
    parser.add_argument("--script-output-max-chars", type=int, default=None)
    parser.add_argument("--turn-timeout", type=float, default=None)
    parser.add_argument("--model-timeout", type=float, default=None)
    parser.add_argument(
        "--no-resume",
        dest="resume",
        action="store_false",
        default=None,
        help="Ignore saved per-task state and start every task from scratch.",
    )
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args(argv)
