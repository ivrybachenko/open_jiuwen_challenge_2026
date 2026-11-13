"""Task model and answer submission."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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
