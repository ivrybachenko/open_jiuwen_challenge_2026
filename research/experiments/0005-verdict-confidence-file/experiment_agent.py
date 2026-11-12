#!/usr/bin/env python3
"""Harness entry point for experiment 0005.

When ``EXP_VERDICT_PROMPT`` is ``soft`` or ``hard`` the system prompt asks the
agent to write ``verdict.txt`` (verdict, confidence, optional comment) in the
same script as ``answer.txt``.  After every turn the file is snapshotted into
the agent directory, so the runner can join it with the evaluator verdict.

The soft prompt was tested first; an 8-task pilot showed that the model usually
ignored it.  The hard prompt repeats the requirement as a mandatory final part
of the script and gives a literal template.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "harness" / "src"))

from harness.application import cli, solver as solver_module  # noqa: E402
from harness.application.solver import BashAgentSolver  # noqa: E402

VERDICT_PROMPT_SOFT = """
Verdict file.

In the same script that produces your answer, also write verdict.txt in the
current directory. It must contain exactly:

  line 1: solved | not_solved | impossible
  line 2: a number from 0.00 to 1.00
  line 3 (optional): one short comment

`solved` means you believe answer.txt contains the correct final answer.
`not_solved` means you could not obtain a reliable answer yet.
`impossible` means you have evidence that the task has no valid answer.

The confidence is the probability that line 1 correctly describes the task:
the task is correctly solved, is genuinely unsolved, or is genuinely
impossible. Write only one of the three exact words on line 1, with no other
text. Write verdict.txt in the same execution; do not spend an extra turn on
it. answer.txt is still required and keeps its usual rules; verdict.txt never
replaces it and is not the submitted answer.
"""

VERDICT_PROMPT_HARD = """
MANDATORY verdict file (do not skip it).

Every script you write must end by creating verdict.txt in the current
directory, even when the task is unsolved or impossible. Use exactly this
shape at the end of the script:

  echo "<solved|not_solved|impossible>" > verdict.txt
  echo "<0.00..1.00>" >> verdict.txt
  echo "<optional one-line comment>" >> verdict.txt

The first line must be one of the three exact words, lowercase:
  solved      answer.txt contains the correct final answer;
  not_solved  no reliable answer was obtained yet;
  impossible  there is evidence that the task has no valid answer.
The second line is the probability that the first line correctly describes
the task: the task is correctly solved, is genuinely unsolved, or is genuinely
impossible. Do not use 1.00 unless you actually verified the result.

Create verdict.txt in the same execution as answer.txt; do not spend an extra
turn on it. answer.txt is still required, keeps its usual rules, and is the
only submitted answer. A script without verdict.txt is incomplete.
"""


def _mode() -> str:
    return os.environ.get("EXP_VERDICT_PROMPT", "0").strip().lower()


if _mode() in {"soft", "1", "true", "yes", "on"}:
    solver_module.SYSTEM_PROMPT = (
        solver_module.SYSTEM_PROMPT + "\n" + VERDICT_PROMPT_SOFT
    )
elif _mode() in {"hard", "2"}:
    solver_module.SYSTEM_PROMPT = (
        solver_module.SYSTEM_PROMPT + "\n" + VERDICT_PROMPT_HARD
    )


class ExperimentSolver(BashAgentSolver):
    """Stock solver that snapshots verdict.txt after each turn."""

    async def run_turn(self, task, state, wave):
        verdict_path = task.workspace / "verdict.txt"
        try:
            verdict_path.unlink(missing_ok=True)
        except OSError:
            pass
        turn = await super().run_turn(task, state, wave)
        try:
            if verdict_path.is_file():
                destination = (
                    self._task_agent_dir(task) / f"verdict_wave{wave}.txt"
                )
                destination.write_text(
                    verdict_path.read_text(encoding="utf-8", errors="replace"),
                    encoding="utf-8",
                )
        except OSError:
            pass
        return turn


def _build_solver(settings):
    return ExperimentSolver(settings)


cli.build_solver = _build_solver


if __name__ == "__main__":
    raise SystemExit(cli.main())
