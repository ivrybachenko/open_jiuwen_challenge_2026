"""Runtime configuration.

Everything the harness knows about the run comes from CLI flags and the
environment variables passed by the jury:

    TASKS         - directory with task folders (``--tasks-dir`` overrides it)
    OUT           - where the solutions file is written
    LLM_BASE_URL  - OpenAI-compatible proxy endpoint
    LLM_API_KEY   - proxy key (never baked into the image)
    LLM_MODEL     - one of the four allowed model names
    TOKEN_BUDGET  - optional output-token budget

The container root filesystem is read-only, so the default output location
and the agent workspace live under ``/tmp``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .llm import DEFAULT_MODEL

DEFAULT_TASKS_DIR = Path("/data/tasks")
DEFAULT_OUT = Path("/tmp/out/solutions.json")
DEFAULT_AGENT_WORKSPACE = Path("/tmp/agent-workspaces")
DEFAULT_MAX_ITERATIONS = 12

_BUDGET_ENV_VARS = ("TOKEN_BUDGET", "BUDGET", "LLM_TOKEN_BUDGET")


def _resolve_out(raw: str | None) -> Path:
    """``OUT`` may point either at a directory or at a file."""
    if not raw:
        return DEFAULT_OUT
    path = Path(raw).expanduser()
    if raw.endswith(("/", os.sep)) or path.is_dir():
        return path / "solutions.json"
    return path


def _int_or_none(raw: str | None) -> int | None:
    if raw is None or not str(raw).strip():
        return None
    try:
        return int(str(raw).strip())
    except ValueError:
        return None


@dataclass(frozen=True)
class Settings:
    tasks_dir: Path
    out: Path
    llm_base_url: str | None
    llm_api_key: str | None
    model: str
    budget: int | None
    max_iterations: int
    agent_workspace: Path

    @classmethod
    def from_env(
        cls,
        *,
        tasks_dir: Path | str | None = None,
        out: Path | str | None = None,
        budget: int | None = None,
        model: str | None = None,
        max_iterations: int | None = None,
        agent_workspace: Path | str | None = None,
    ) -> "Settings":
        env = os.environ
        raw_tasks = str(tasks_dir) if tasks_dir is not None else env.get("TASKS")
        raw_out = str(out) if out is not None else env.get("OUT")
        tasks_path = Path(raw_tasks) if raw_tasks else DEFAULT_TASKS_DIR
        # Without OUT the tasks mount is the only writable persistent place.
        resolved_out = _resolve_out(raw_out) if raw_out else tasks_path / "solutions.json"

        if budget is None:
            budget = next(
                (
                    parsed
                    for name in _BUDGET_ENV_VARS
                    if (parsed := _int_or_none(env.get(name))) is not None
                ),
                None,
            )
        if max_iterations is None:
            max_iterations = _int_or_none(env.get("MAX_ITERATIONS")) or DEFAULT_MAX_ITERATIONS

        raw_workspace = (
            str(agent_workspace)
            if agent_workspace is not None
            else env.get("AGENT_WORKSPACE")
        )

        return cls(
            tasks_dir=tasks_path,
            out=resolved_out,
            llm_base_url=env.get("LLM_BASE_URL"),
            llm_api_key=env.get("LLM_API_KEY"),
            model=model or env.get("LLM_MODEL") or DEFAULT_MODEL,
            budget=budget,
            max_iterations=max_iterations,
            agent_workspace=(
                Path(raw_workspace) if raw_workspace else DEFAULT_AGENT_WORKSPACE
            ),
        )
