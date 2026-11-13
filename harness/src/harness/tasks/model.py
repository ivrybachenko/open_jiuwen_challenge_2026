"""Task model and answer submission."""

from __future__ import annotations

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

    def contains(self, path: Path) -> bool:
        """True when ``path`` resolves inside this task directory.

        The agent can create symlinks, and a symlinked ``workspace/`` could
        otherwise move the harness outside the mounted task directory.  The
        check is deliberately done on resolved paths.
        """
        try:
            return Path(path).resolve().is_relative_to(self.root.resolve())
        except (OSError, RuntimeError):
            return False

    @property
    def workspace(self) -> Path:
        """Directory the agent works in (``cwd`` for the solver)."""
        workspace = self.root / "workspace"
        if workspace.is_dir() and self.contains(workspace):
            return workspace
        return self.root

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

    def read_answer(self, max_chars: int | None = None) -> str | None:
        """Read the first non-empty answer that is safe to read.

        ``answer.txt`` may be a symlink created by the agent.  A link that
        resolves outside the task directory is ignored, the same as a missing
        file.
        """
        for path in self.answer_paths:
            if not self.contains(path):
                log.warning(
                    "ignoring answer.txt outside the task directory: %s", path
                )
                continue
            try:
                with path.open("r", encoding="utf-8", errors="replace") as stream:
                    text = stream.read() if max_chars is None else stream.read(
                        max_chars + 1
                    )
            except OSError:
                continue
            if text.strip():
                return text
        return None

    def write_answer(self, text: str) -> None:
        payload = text if text.endswith("\n") else f"{text}\n"
        errors: list[OSError] = []
        written = 0
        for path in self.answer_paths:
            if not self.contains(path):
                log.warning(
                    "not writing answer.txt outside the task directory: %s", path
                )
                continue
            try:
                path.write_text(payload, encoding="utf-8")
                written += 1
            except OSError as exc:  # pragma: no cover - depends on the mount
                errors.append(exc)
        if written == 0 and errors:
            raise errors[0]
        if written == 0 and not errors:
            raise OSError(f"no safe answer path for {self.task_id}")
