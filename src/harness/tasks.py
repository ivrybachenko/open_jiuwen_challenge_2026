"""Task discovery and answer submission."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Task:
    task_id: str
    task_type: str
    instruction: str
    reward: float
    expected: str | None
    check: str | None
    root: Path

    @property
    def workspace(self) -> Path:
        """Directory the agent works in (``cwd`` for the solver)."""
        workspace = self.root / "workspace"
        return workspace if workspace.is_dir() else self.root

    @property
    def answer_paths(self) -> tuple[Path, ...]:
        """Where ``answer.txt`` may be expected.

        The regulation says "in the task directory", while each instruction
        says "in the current directory" (= ``workspace/``). Writing both is
        cheap and removes the ambiguity.
        """
        paths = [self.workspace / "answer.txt"]
        if self.root != self.workspace:
            paths.append(self.root / "answer.txt")
        return tuple(paths)

    def write_answer(self, text: str) -> None:
        payload = text if text.endswith("\n") else f"{text}\n"
        errors: list[OSError] = []
        for path in self.answer_paths:
            try:
                path.write_text(payload, encoding="utf-8")
            except OSError as exc:  # pragma: no cover - depends on the mount
                errors.append(exc)
        if len(errors) == len(self.answer_paths):
            raise errors[0]


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
