"""Repository locations used by the evaluation CLIs."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Root of the challenge repository (``.../open_jiuwen_challenge_2026``)."""
    return Path(__file__).resolve().parents[2]


def default_tasks_root() -> Path:
    return repo_root() / "data" / "task"


def default_task_set_dir() -> Path:
    return repo_root() / "data" / "task_set"


def default_out_dir() -> Path:
    return repo_root() / "out" / "reports"


def resolve_path(raw: str | Path | None, *, base: Path | None = None) -> Path | None:
    """Expand ``~`` and resolve a relative path against ``base`` (or cwd)."""
    if raw is None:
        return None
    path = Path(raw).expanduser()
    if not path.is_absolute() and base is not None:
        path = base / path
    return path.resolve()


def resolve_task_set_path(raw: str | Path) -> Path:
    """Resolve a task-set file against cwd, ``data/task_set`` and the repo root."""
    path = Path(raw).expanduser()
    if path.is_absolute():
        candidates = [path]
    else:
        candidates = [
            Path.cwd() / path,
            default_task_set_dir() / path,
            repo_root() / path,
        ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(f"task-set file not found: {raw}")
