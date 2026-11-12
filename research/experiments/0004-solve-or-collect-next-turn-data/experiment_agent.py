#!/usr/bin/env python3
"""Harness entry point for experiment 0004.

The shipped harness is not modified.  When ``EXP_GOAL_PROMPT=1`` this entry
point appends a two-turn goal instruction to the system prompt: solve the task
in one turn if possible, otherwise spend the turn collecting the maximum useful
data for the next one.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "harness" / "src"))

from harness.application import cli, solver as solver_module  # noqa: E402
from harness.application.solver import BashAgentSolver  # noqa: E402

GOAL_PROMPT = """
Two-turn goal.

Before writing the script, decide which case you are in.

1. The task can be finished with the information you already have. Then the
   script must inspect, compute, edit and submit the final answer.txt in one
   execution. Prefer this case.

2. The task cannot be finished safely yet: you need data that only the script
   can obtain (file contents, dataset schema, exact failing test, version or
   command output). Then the script must collect the maximum useful data for
   the next turn in one execution, not a single narrow probe. Read the relevant
   files or a representative sample, print exact errors and the values you will
   need. The harness truncates the output to 4000 characters, so print the most
   valuable data first and keep it compact.

Never spend a whole turn on a single `ls`, `head`, `grep` or `cat`.
Do not submit a guessed answer, and do not write IMPOSSIBLE until you have
evidence that the task is impossible.
"""


def _enabled(name: str) -> bool:
    return os.environ.get(name, "0").strip().lower() in {"1", "true", "yes", "on"}


if _enabled("EXP_GOAL_PROMPT"):
    solver_module.SYSTEM_PROMPT = solver_module.SYSTEM_PROMPT + "\n" + GOAL_PROMPT


class ExperimentSolver(BashAgentSolver):
    """Stock bash solver; the prompt is the only changed behaviour."""


def _build_solver(settings):
    return ExperimentSolver(settings)


cli.build_solver = _build_solver


if __name__ == "__main__":
    raise SystemExit(cli.main())
