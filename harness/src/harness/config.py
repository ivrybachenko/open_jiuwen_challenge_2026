"""Runtime configuration.

Everything the harness knows about the run comes from CLI flags and the
environment variables passed by the jury:

    TASKS         - directory with task folders (``--tasks-dir`` overrides it)
    OUT           - where the solutions file is written
    LLM_BASE_URL  - OpenAI-compatible proxy endpoint
    LLM_API_KEY   - proxy key (never baked into the image)
    LLM_MODEL     - one of the four allowed model names
    BUDGET        - output-token budget (default 100000)
    HARNESS_MAX_WAVES - wave 1 plus follow-up waves (default 8)
    TRAJECTORIES_DIR - optional directory for attempt logs
    HARNESS_RUN_ID - optional run identifier stored in the attempt log

The container root filesystem is read-only, so the default output location
and the agent workspace live under ``/tmp``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from harness.infrastructure.llm import DEFAULT_MODEL

DEFAULT_TASKS_DIR = Path("/data/tasks")
DEFAULT_OUT = Path("/tmp/out/solutions.json")
DEFAULT_AGENT_WORKSPACE = Path("/tmp/agent-workspaces")
DEFAULT_MAX_ITERATIONS = 12

# Harness v0003 behaviour.  Values are exposed as flags so the evaluators can
# compare strategies without editing code.
DEFAULT_WAVE1_MAX_TOKENS = 1000
DEFAULT_WAVE2_MAX_TOKENS = 4000
DEFAULT_WAVE2_MAX_TASKS = 50
DEFAULT_MAX_WAVES = 8
DEFAULT_OVERVIEW_MAX_TOKENS = 1500
DEFAULT_SCRIPT_OUTPUT_MAX_CHARS = 4000
DEFAULT_TURN_TIMEOUT = 120.0
DEFAULT_MODEL_TIMEOUT = 180.0
DEFAULT_TOKEN_BUDGET = 100_000

_BUDGET_ENV_VARS = ("BUDGET",)


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


def _float_or_none(raw: str | None) -> float | None:
    if raw is None or not str(raw).strip():
        return None
    try:
        return float(str(raw).strip())
    except ValueError:
        return None


def _first_int(env: dict[str, str], names: tuple[str, ...]) -> int | None:
    for name in names:
        parsed = _int_or_none(env.get(name))
        if parsed is not None:
            return parsed
    return None


def _first_float(env: dict[str, str], names: tuple[str, ...]) -> float | None:
    for name in names:
        parsed = _float_or_none(env.get(name))
        if parsed is not None:
            return parsed
    return None


@dataclass(frozen=True)
class Settings:
    tasks_dir: Path
    out: Path
    llm_base_url: str | None
    llm_api_key: str | None
    model: str
    budget: int
    max_iterations: int
    agent_workspace: Path
    trajectories_dir: Path | None
    run_id: str | None
    wave2_model: str | None = None
    wave1_max_tokens: int = DEFAULT_WAVE1_MAX_TOKENS
    wave2_max_tokens: int = DEFAULT_WAVE2_MAX_TOKENS
    wave2_max_tasks: int = DEFAULT_WAVE2_MAX_TASKS
    max_waves: int = DEFAULT_MAX_WAVES
    overview_max_tokens: int = DEFAULT_OVERVIEW_MAX_TOKENS
    script_output_max_chars: int = DEFAULT_SCRIPT_OUTPUT_MAX_CHARS
    turn_timeout: float = DEFAULT_TURN_TIMEOUT
    model_timeout: float = DEFAULT_MODEL_TIMEOUT
    resume: bool = True

    @classmethod
    def from_env(
        cls,
        *,
        tasks_dir: Path | str | None = None,
        out: Path | str | None = None,
        budget: int | None = None,
        model: str | None = None,
        wave2_model: str | None = None,
        max_iterations: int | None = None,
        agent_workspace: Path | str | None = None,
        trajectories_dir: Path | str | None = None,
        run_id: str | None = None,
        wave1_max_tokens: int | None = None,
        wave2_max_tokens: int | None = None,
        wave2_max_tasks: int | None = None,
        max_waves: int | None = None,
        overview_max_tokens: int | None = None,
        script_output_max_chars: int | None = None,
        turn_timeout: float | None = None,
        model_timeout: float | None = None,
        resume: bool | None = None,
    ) -> "Settings":
        env = dict(os.environ)
        raw_tasks = str(tasks_dir) if tasks_dir is not None else env.get("TASKS")
        raw_out = str(out) if out is not None else env.get("OUT")
        tasks_path = Path(raw_tasks) if raw_tasks else DEFAULT_TASKS_DIR
        # Without OUT the tasks mount is the only writable persistent place.
        resolved_out = _resolve_out(raw_out) if raw_out else tasks_path / "solutions.json"

        if budget is None:
            budget = _first_int(env, _BUDGET_ENV_VARS)
        if budget is None:
            budget = DEFAULT_TOKEN_BUDGET
        if max_iterations is None:
            max_iterations = _int_or_none(env.get("MAX_ITERATIONS")) or DEFAULT_MAX_ITERATIONS

        raw_workspace = (
            str(agent_workspace)
            if agent_workspace is not None
            else env.get("AGENT_WORKSPACE")
        )
        raw_trajectories = (
            str(trajectories_dir)
            if trajectories_dir is not None
            else env.get("TRAJECTORIES_DIR")
        )
        raw_run_id = (
            str(run_id) if run_id is not None else env.get("HARNESS_RUN_ID")
        )
        resolved_model = model or env.get("LLM_MODEL") or DEFAULT_MODEL
        resolved_wave2_model = (
            wave2_model
            or env.get("LLM_WAVE2_MODEL")
            or resolved_model
        )

        if wave1_max_tokens is None:
            wave1_max_tokens = (
                _first_int(env, ("HARNESS_WAVE1_MAX_TOKENS",))
                or DEFAULT_WAVE1_MAX_TOKENS
            )
        if wave2_max_tokens is None:
            wave2_max_tokens = (
                _first_int(env, ("HARNESS_WAVE2_MAX_TOKENS",))
                or DEFAULT_WAVE2_MAX_TOKENS
            )
        if wave2_max_tasks is None:
            wave2_max_tasks = (
                _first_int(env, ("HARNESS_WAVE2_MAX_TASKS",))
                or DEFAULT_WAVE2_MAX_TASKS
            )
        if overview_max_tokens is None:
            overview_max_tokens = (
                _first_int(env, ("HARNESS_OVERVIEW_MAX_TOKENS",))
                or DEFAULT_OVERVIEW_MAX_TOKENS
            )
        if max_waves is None:
            max_waves = (
                _first_int(env, ("HARNESS_MAX_WAVES",))
                or DEFAULT_MAX_WAVES
            )
        if script_output_max_chars is None:
            script_output_max_chars = (
                _first_int(env, ("HARNESS_SCRIPT_OUTPUT_MAX_CHARS",))
                or DEFAULT_SCRIPT_OUTPUT_MAX_CHARS
            )
        if turn_timeout is None:
            turn_timeout = (
                _first_float(env, ("HARNESS_TURN_TIMEOUT",))
                or DEFAULT_TURN_TIMEOUT
            )
        if model_timeout is None:
            model_timeout = (
                _first_float(env, ("HARNESS_MODEL_TIMEOUT",))
                or DEFAULT_MODEL_TIMEOUT
            )
        if resume is None:
            resume = env.get("HARNESS_RESUME", "1").strip().lower() not in {
                "0",
                "false",
                "no",
                "off",
            }

        return cls(
            tasks_dir=tasks_path,
            out=resolved_out,
            llm_base_url=env.get("LLM_BASE_URL"),
            llm_api_key=env.get("LLM_API_KEY"),
            model=resolved_model,
            wave2_model=resolved_wave2_model,
            budget=budget,
            max_iterations=max_iterations,
            agent_workspace=(
                Path(raw_workspace) if raw_workspace else DEFAULT_AGENT_WORKSPACE
            ),
            trajectories_dir=(
                Path(raw_trajectories).expanduser() if raw_trajectories else None
            ),
            run_id=raw_run_id.strip() if raw_run_id and raw_run_id.strip() else None,
            wave1_max_tokens=max(1, int(wave1_max_tokens)),
            wave2_max_tokens=max(1, int(wave2_max_tokens)),
            wave2_max_tasks=max(0, int(wave2_max_tasks)),
            max_waves=max(1, int(max_waves)),
            overview_max_tokens=max(200, int(overview_max_tokens)),
            script_output_max_chars=max(200, int(script_output_max_chars)),
            turn_timeout=max(1.0, float(turn_timeout)),
            model_timeout=max(1.0, float(model_timeout)),
            resume=bool(resume),
        )
