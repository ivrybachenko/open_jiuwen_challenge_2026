"""Solutions file: a snapshot persisted after every solved task.

Missing a single flush loses the task, so every ``record()`` call rewrites the
file atomically (write to a sibling temp file, then ``os.replace``).
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger(__name__)


@dataclass
class Solution:
    task_id: str
    reward: float
    solved: bool
    answer: str | None
    input_tokens: int
    output_tokens: int
    cost: int
    note: str
    updated_at: str


class SolutionsStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._solutions: dict[str, dict] = {}
        self._load()

    @property
    def total_score(self) -> float:
        return sum(
            float(item.get("reward", 0))
            for item in self._solutions.values()
            if item.get("solved")
        )

    @property
    def total_cost(self) -> int:
        return sum(int(item.get("cost", 0)) for item in self._solutions.values())

    @property
    def total_input_tokens(self) -> int:
        return sum(
            int(item.get("input_tokens", 0)) for item in self._solutions.values()
        )

    @property
    def total_output_tokens(self) -> int:
        return sum(
            int(item.get("output_tokens", 0)) for item in self._solutions.values()
        )

    def record(self, solution: Solution) -> None:
        self._solutions[solution.task_id] = asdict(solution)
        self._flush()

    def _load(self) -> None:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return
        except (OSError, json.JSONDecodeError) as exc:
            log.warning("cannot read %s (%s); starting empty", self.path, exc)
            return
        if isinstance(payload, dict):
            self._solutions = {
                str(key): value
                for key, value in payload.get("solutions", {}).items()
                if isinstance(value, dict)
            }

    def _flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "total_score": self.total_score,
            "total_cost": self.total_cost,
            "solutions": self._solutions,
        }
        tmp = self.path.with_name(f".{self.path.name}.tmp")
        tmp.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(tmp, self.path)
