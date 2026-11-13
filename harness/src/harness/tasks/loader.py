"""Read task directories from disk.

One malformed task must never stop the run: the jury mounts a hidden set, and a
single unexpected ``reward`` or a byte-order mark should cost at most that task.
"""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any

from harness.tasks.model import Task

log = logging.getLogger(__name__)


def load_tasks(tasks_dir: Path) -> list[Task]:
    """Load every ``<tasks_dir>/*/task.json``, skipping malformed folders."""
    if not tasks_dir.is_dir():
        raise FileNotFoundError(f"tasks directory not found: {tasks_dir}")

    tasks: list[Task] = []
    seen: dict[str, Path] = {}
    for root in sorted(tasks_dir.iterdir()):
        payload_path = root / "task.json"
        try:
            if not payload_path.is_file():
                continue
            if not _inside(root, payload_path):
                log.warning(
                    "skipping %s: task.json points outside the task directory",
                    root.name,
                )
                continue
            # ``utf-8-sig`` accepts both plain UTF-8 and UTF-8 with a BOM.
            payload = json.loads(payload_path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
            log.warning("skipping %s: cannot read task.json (%s)", root.name, exc)
            continue
        if not isinstance(payload, dict):
            log.warning(
                "skipping %s: task.json must be a JSON object, got %s",
                root.name,
                type(payload).__name__,
            )
            continue

        try:
            task_id = _text(payload.get("task_id")) or root.name
            task = Task(
                task_id=task_id,
                task_type=_text(payload.get("task_type")) or "unknown",
                instruction=_text(payload.get("instruction")),
                reward=_reward(payload.get("reward"), root),
                expected=payload.get("expected"),
                check=payload.get("check"),
                root=root,
            )
        except (TypeError, ValueError, OverflowError, RecursionError) as exc:
            log.warning("skipping %s: invalid task fields (%s)", root.name, exc)
            continue

        previous = seen.get(task.task_id)
        if previous is not None:
            log.warning(
                "duplicate task_id %r in %s and %s; solutions and state are "
                "keyed by task_id",
                task.task_id,
                previous,
                root,
            )
        seen[task.task_id] = root
        tasks.append(task)
    if not tasks:
        log.warning("no readable tasks found in %s", tasks_dir)
    return tasks


def _inside(root: Path, path: Path) -> bool:
    """True when ``path`` resolves inside the task directory."""
    try:
        return Path(path).resolve().is_relative_to(root.resolve())
    except (OSError, RuntimeError):
        return False


def _text(value: Any) -> str:
    """Return a string field without letting a wrong JSON type raise."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _reward(value: Any, root: Path) -> float:
    """Parse the points field; an invalid value must not abort the run."""
    try:
        reward = float(value or 0)
    except (TypeError, ValueError, OverflowError):
        log.warning(
            "task %s: invalid reward %r; using 0", root.name, value
        )
        return 0.0
    if not math.isfinite(reward) or reward < 0:
        log.warning(
            "task %s: invalid reward %r; using 0", root.name, value
        )
        return 0.0
    return reward
