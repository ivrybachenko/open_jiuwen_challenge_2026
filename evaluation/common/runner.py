"""Run the harness as a subprocess and read its ``solutions.json``."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

# The evaluators talk to the NeuralDeep proxy directly.  The harness itself
# deliberately contains no URL: it only reads LLM_BASE_URL from the environment.
DEFAULT_LLM_BASE_URL = "https://api.neuraldeep.ru/v1"


@dataclass(frozen=True)
class HarnessConfig:
    repo_root: Path
    python: str | None = None
    model: str | None = None
    budget: int | None = None
    max_iterations: int | None = None
    extra_args: tuple[str, ...] = ()
    timeout: float | None = 3600.0
    env: Mapping[str, str] = field(default_factory=dict)


@dataclass
class HarnessRun:
    command: list[str]
    returncode: int
    duration_seconds: float
    stdout: str
    stderr: str
    out_path: Path
    solutions: dict[str, dict]
    timed_out: bool = False


def resolve_python(config: HarnessConfig) -> str:
    """Pick the interpreter that has ``openjiuwen`` installed.

    Order: explicit ``--python``, ``HARNESS_PYTHON``, ``harness/.venv/bin/python``,
    then the current interpreter.
    """
    if config.python:
        return config.python
    env_python = os.environ.get("HARNESS_PYTHON")
    if env_python:
        return env_python
    venv_python = config.repo_root / "harness" / ".venv" / "bin" / "python"
    if venv_python.is_file():
        return str(venv_python)
    return sys.executable


def missing_llm_env(env: Mapping[str, str] | None = None) -> list[str]:
    """The evaluators supply LLM_BASE_URL themselves; only the key is required."""
    env = os.environ if env is None else env
    return ["LLM_API_KEY"] if not env.get("LLM_API_KEY") else []


def read_solutions(path: str | Path) -> dict[str, dict]:
    """Read the ``solutions.json`` payload produced by the harness."""
    path = Path(path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    raw = payload.get("solutions", payload)
    if not isinstance(raw, dict):
        return {}
    return {
        str(task_id): value
        for task_id, value in raw.items()
        if isinstance(value, dict)
    }


def run_harness(
    config: HarnessConfig,
    tasks_dir: str | Path,
    out_path: str | Path,
) -> HarnessRun:
    """Execute ``python -m harness.run_agent`` against a flat tasks directory."""
    out_path = Path(out_path).resolve()
    tasks_dir = Path(tasks_dir).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        resolve_python(config),
        "-m",
        "harness.run_agent",
        "--tasks-dir",
        str(tasks_dir),
        "--out",
        str(out_path),
    ]
    if config.model:
        command += ["--model", config.model]
    if config.budget is not None:
        command += ["--budget", str(config.budget)]
    if config.max_iterations is not None:
        command += ["--max-iterations", str(config.max_iterations)]
    command += list(config.extra_args)

    env = os.environ.copy()
    env.update({str(key): str(value) for key, value in config.env.items()})
    env.setdefault("PYTHONUNBUFFERED", "1")
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    # The URL lives in the evaluator, not in the harness.
    if not env.get("LLM_BASE_URL"):
        env["LLM_BASE_URL"] = DEFAULT_LLM_BASE_URL
    src = config.repo_root / "harness" / "src"
    env["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(src), env.get("PYTHONPATH", "")) if part
    )

    started = time.monotonic()
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            cwd=str(config.repo_root),
            env=env,
            capture_output=True,
            text=True,
            timeout=config.timeout,
        )
        returncode = completed.returncode
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = 124
        stdout = _as_text(exc.stdout)
        stderr = _as_text(exc.stderr)
        stderr += f"\n[timeout after {config.timeout}s]"
    except FileNotFoundError as exc:
        returncode = 127
        stdout = ""
        stderr = f"{type(exc).__name__}: {exc}"
    duration = time.monotonic() - started

    return HarnessRun(
        command=command,
        returncode=returncode,
        duration_seconds=duration,
        stdout=stdout,
        stderr=stderr,
        out_path=out_path,
        solutions=read_solutions(out_path),
        timed_out=timed_out,
    )


def _as_text(value: bytes | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value
