"""Read task directories from disk."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from harness.domain.tasks import Task

log = logging.getLogger(__name__)


def load_tasks(tasks_dir: Path) -> list[Task]:
    """Load every ``<tasks_dir>/*/task.json``, skipping malformed folders."""
    if not tasks_dir.is_dir():
        raise FileNotFoundError(f"tasks directory not found: {tasks_dir}")

    tasks: list[Task] = []
    for root in sorted(tasks_dir.iterdir()):
        payload_path = root / "task.json"
        if not payload_path.is_file():
            continue
        try:
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            log.warning("skipping %s: cannot read task.json (%s)", root.name, exc)
            continue

        tasks.append(
            Task(
                task_id=str(payload.get("task_id") or root.name),
                task_type=str(payload.get("task_type") or "unknown"),
                instruction=str(payload.get("instruction") or ""),
                reward=float(payload.get("reward") or 0),
                expected=payload.get("expected"),
                check=payload.get("check"),
                root=root,
            )
        )
    return tasks
