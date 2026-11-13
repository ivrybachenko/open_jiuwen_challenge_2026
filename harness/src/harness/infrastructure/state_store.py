"""Atomic JSON persistence for per-task state."""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
from pathlib import Path

from harness.config import Settings
from harness.domain.state import TaskState
from harness.domain.tasks import Task

log = logging.getLogger(__name__)

STATE_FILE = "state.json"
STATE_VERSION = 2


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
