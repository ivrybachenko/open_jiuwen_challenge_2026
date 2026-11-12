#!/usr/bin/env python3
"""Harness entry point with experiment-only options for experiment 0003.

The shipped harness is not modified.  This entry point imports it, replaces the
solver factory with a subclass that can use a different model in each wave and
optionally allows an explanation block around the bash script.

Environment variables
---------------------
EXP_WAVE2_MODEL
    Model used in wave 2.  Defaults to ``--model`` (a normal harness run).
EXP_EXPLAIN
    ``1`` appends an explanation-block instruction to the system prompt.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "harness" / "src"))

from harness.application import cli, solver as solver_module  # noqa: E402
from harness.application.solver import BashAgentSolver  # noqa: E402

EXPLAIN_PROMPT = """
Explanation block (allowed in this experiment).

You may write a short explanation of your plan and findings before or after
the script. Put the complete bash script in a fenced block that starts with
```bash and ends with ```. The harness executes only the contents of the LAST
fenced block; if the explanation goes after the script, do not use another
fenced block there. The explanation is not executed: answer.txt and the task
files must still be produced by the script itself, exactly as before.
"""

EXPLAIN_PROMPT_SINGLE = """
Explanation block (single-script experiment).

You may write a short explanation of your plan and findings before or after
the script. Your reply must contain EXACTLY ONE fenced block, and that block
must be the complete bash script for this turn. Do not put exploratory
commands in separate fenced blocks: put them inside the same script or
describe them in the explanation. The harness executes the content of that
single fenced block. The explanation is not executed: answer.txt and the task
files must still be produced by the script itself, exactly as before.
"""

EXPLAIN_PROMPT_SINGLE_ONLY = """
Single-script format (ablation, no explanation).

Reply with exactly one fenced bash block containing the complete script for
this turn. Do not write any text before or after the block. The harness
executes the contents of that block.
"""

_EXPLAIN_MODE = os.environ.get("EXP_EXPLAIN", "0").strip().lower()
if _EXPLAIN_MODE in {"1", "allowed", "true", "yes"}:
    solver_module.SYSTEM_PROMPT = solver_module.SYSTEM_PROMPT + "\n" + EXPLAIN_PROMPT
elif _EXPLAIN_MODE in {"single", "2"}:
    solver_module.SYSTEM_PROMPT = solver_module.SYSTEM_PROMPT + "\n" + EXPLAIN_PROMPT_SINGLE
elif _EXPLAIN_MODE in {"single-only", "3"}:
    solver_module.SYSTEM_PROMPT = solver_module.SYSTEM_PROMPT + "\n" + EXPLAIN_PROMPT_SINGLE_ONLY


class ExperimentSolver(BashAgentSolver):
    """Bash solver with a separate model for wave 2."""

    def __init__(self, settings) -> None:
        super().__init__(settings)
        self.wave2_model_name = (
            os.environ.get("EXP_WAVE2_MODEL", "").strip() or settings.model
        )
        self.search_wave1_model_name = os.environ.get(
            "EXP_SEARCH_WAVE1_MODEL", ""
        ).strip()
        self._wave1_handle = None
        self._wave2_handle = None
        self._search_wave1_handle = None

    async def start(self) -> None:
        await super().start()
        self._wave1_handle = self._model

        from openjiuwen.core.foundation.llm import init_model

        def init(name: str):
            return init_model(
                provider="OpenAI",
                model_name=name,
                api_key=self.settings.llm_api_key or "",
                api_base=self.settings.llm_base_url or "",
                timeout=self.settings.model_timeout,
                max_retries=1,
                verify_ssl=True,
            )

        if self.wave2_model_name == self.settings.model:
            self._wave2_handle = self._wave1_handle
        else:
            self._wave2_handle = init(self.wave2_model_name)

        if not self.search_wave1_model_name:
            self._search_wave1_handle = self._wave1_handle
        elif self.search_wave1_model_name == self.settings.model:
            self._search_wave1_handle = self._wave1_handle
        elif self.search_wave1_model_name == self.wave2_model_name:
            self._search_wave1_handle = self._wave2_handle
        else:
            self._search_wave1_handle = init(self.search_wave1_model_name)

    async def run_turn(self, task, state, wave):
        if wave == 1:
            self._model = (
                self._search_wave1_handle
                if task.task_type == "search"
                else self._wave1_handle
            )
        else:
            self._model = self._wave2_handle
        return await super().run_turn(task, state, wave)


def _build_experiment_solver(settings):
    return ExperimentSolver(settings)


cli.build_solver = _build_experiment_solver


if __name__ == "__main__":
    raise SystemExit(cli.main())
