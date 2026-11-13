"""Answer value object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnswerInfo:
    text: str | None
    kind: str
    first_line: str = ""

    @property
    def present(self) -> bool:
        return self.text is not None
