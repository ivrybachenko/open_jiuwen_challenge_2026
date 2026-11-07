"""Runtime configuration.

Everything the harness knows about the run comes from CLI flags and the
environment variables passed by the jury:

    TASKS         - directory with task folders (``--tasks-dir`` overrides it)
    OUT           - where the solutions file is written
    LLM_BASE_URL  - OpenAI-compatible proxy endpoint
    LLM_API_KEY   - proxy key (never baked into the image)

The container root filesystem is read-only, so the default output location
lives under ``/tmp``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_TASKS_DIR = Path("/data/tasks")
DEFAULT_OUT = Path("/tmp/out/solutions.json")


def _resolve_out(raw: str | None) -> Path:
    """``OUT`` may point either at a directory or at a file."""
    if not raw:
        return DEFAULT_OUT
    path = Path(raw).expanduser()
    if raw.endswith(("/", os.sep)) or path.is_dir():
        return path / "solutions.json"
    return path


@dataclass(frozen=True)
class Settings:
    tasks_dir: Path
    out: Path
    llm_base_url: str | None
    llm_api_key: str | None
    budget: int | None

    @classmethod
    def from_env(
        cls,
        *,
        tasks_dir: Path | str | None = None,
        out: Path | str | None = None,
        budget: int | None = None,
    ) -> "Settings":
        env = os.environ
        raw_tasks = str(tasks_dir) if tasks_dir is not None else env.get("TASKS")
        raw_out = str(out) if out is not None else env.get("OUT")
        tasks_path = Path(raw_tasks) if raw_tasks else DEFAULT_TASKS_DIR
        # Without OUT the tasks mount is the only writable persistent place.
        resolved_out = _resolve_out(raw_out) if raw_out else tasks_path / "solutions.json"
        return cls(
            tasks_dir=tasks_path,
            out=resolved_out,
            llm_base_url=env.get("LLM_BASE_URL"),
            llm_api_key=env.get("LLM_API_KEY"),
            budget=budget,
        )
