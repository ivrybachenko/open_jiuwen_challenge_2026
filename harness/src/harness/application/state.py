"""Per-task state and its atomic JSON store."""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

from harness.application.config import Settings
from harness.application.tasks import Task

log = logging.getLogger(__name__)

STATE_FILE = "state.json"
STATE_VERSION = 2


@dataclass
class TaskState:
    task_id: str
    task_root: str
    model: str
    wave2_model: str = ""
    overview: str = ""
    messages: list[dict[str, Any]] = field(default_factory=list)
    turns: list[dict[str, Any]] = field(default_factory=list)
    answer: str | None = None
    answer_kind: str = "none"
    wave1_done: bool = False
    wave2_done: bool = False
    impossible_declared: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    cost: int = 0
    last_error: str = ""
    selected_wave2: bool = False
    promise: float = 0.0

    def wave_done(self, wave: int) -> bool:
        """True when this wave already produced a turn."""
        if wave == 1 and self.wave1_done:
            return True
        if wave == 2 and self.wave2_done:
            return True
        return any(
            int(turn.get("wave", 0) or 0) == wave for turn in self.turns
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TaskState":
        known = {item.name for item in fields(cls)}
        return cls(**{key: value for key, value in payload.items() if key in known})


class StateStore:
    """Load, save and reset per-task state under the agent workspace."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def agent_dir(self, task: Task) -> Path:
        return self.settings.agent_workspace / _safe_name(task.task_id)

    def path(self, task: Task) -> Path:
        return self.agent_dir(task) / STATE_FILE

    def reset(self, task: Task) -> None:
        agent_dir = self.agent_dir(task)
        shutil.rmtree(agent_dir, ignore_errors=True)
        agent_dir.mkdir(parents=True, exist_ok=True)

    def ensure_dir(self, task: Task) -> None:
        self.agent_dir(task).mkdir(parents=True, exist_ok=True)

    def load(self, task: Task) -> TaskState | None:
        if not self.settings.resume:
            return None
        try:
            payload = json.loads(self.path(task).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if payload.get("version") != STATE_VERSION:
            return None
        raw = payload.get("state")
        if not isinstance(raw, dict):
            return None
        if raw.get("task_root") != str(task.root):
            return None
        if raw.get("model") != self.settings.model:
            return None
        state_wave2 = raw.get("wave2_model") or raw.get("model")
        if state_wave2 != (self.settings.wave2_model or self.settings.model):
            return None
        try:
            state = TaskState.from_dict(raw)
        except (TypeError, ValueError):
            return None
        if not state.messages:
            return None
        return state

    def save(self, task: Task, state: TaskState) -> None:
        path = self.path(task)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_name(f".{path.name}.tmp")
            tmp.write_text(
                json.dumps(
                    {"version": STATE_VERSION, "state": state.to_dict()},
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            os.replace(tmp, path)
        except (OSError, TypeError, ValueError):
            log.warning("cannot save state for %s", state.task_id, exc_info=True)

    def clear_answers(self, task: Task) -> None:
        for path in task.answer_paths:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                log.debug("cannot remove stale %s", path, exc_info=True)


def _safe_name(value: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "unknown")).strip("._-")
    return stem or "unknown"
