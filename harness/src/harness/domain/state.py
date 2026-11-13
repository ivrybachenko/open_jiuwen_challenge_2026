"""Per-task state model."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from typing import Any


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
