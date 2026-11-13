"""Answer contract: value object and classification."""

from __future__ import annotations

from dataclasses import dataclass

DONE_VALUES = {"DONE", "OK", "SUCCESS", "PASS", "TESTS PASS"}


@dataclass(frozen=True)
class AnswerInfo:
    text: str | None
    kind: str
    first_line: str = ""

    @property
    def present(self) -> bool:
        return self.text is not None


def classify_answer(text: str | None) -> AnswerInfo:
    if text is None or not text.strip():
        return AnswerInfo(text=None, kind="none")
    stripped = text.strip()
    first_line = stripped.splitlines()[0].strip()
    if first_line.upper().startswith("IMPOSSIBLE"):
        return AnswerInfo(text=stripped, kind="impossible", first_line=first_line)
    if stripped.upper() in DONE_VALUES:
        return AnswerInfo(text=stripped, kind="done", first_line=first_line)
    return AnswerInfo(text=stripped, kind="value", first_line=first_line)
