"""Solutions file: a snapshot persisted after every solved task.

Missing a single flush loses the task, so every ``record()`` call rewrites the
file atomically (write to a sibling temp file, then ``os.replace``).

The jury may set ``OUT`` to a path that is not writable inside the read-only
container (the run command in the regulation does not mount it).  A failed
flush must not stop the run, so the store falls back to the tasks directory and
then to ``/tmp``; the path that actually worked is reused for later writes.
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
    def __init__(self, path: Path, fallbacks: tuple[Path, ...] = ()) -> None:
        self.path = Path(path)
        self._fallbacks = tuple(Path(item) for item in fallbacks)
        self._solutions: dict[str, dict] = {}
        self._load()

    @property
    def candidates(self) -> tuple[Path, ...]:
        """The current path followed by the configured fallbacks, deduplicated."""
        seen: list[Path] = []
        for item in (self.path, *self._fallbacks):
            if item not in seen:
                seen.append(item)
        return tuple(seen)

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
        for path in self.candidates:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except FileNotFoundError:
                continue
            except (OSError, json.JSONDecodeError) as exc:
                log.warning("cannot read %s (%s); trying the next path", path, exc)
                continue
            if isinstance(payload, dict):
                self._solutions = {
                    str(key): value
                    for key, value in payload.get("solutions", {}).items()
                    if isinstance(value, dict)
                }
                if path != self.path:
                    log.warning("resuming from fallback solutions file %s", path)
                    self.path = path
            return

    def _flush(self) -> None:
        payload = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "total_score": self.total_score,
            "total_cost": self.total_cost,
            "solutions": self._solutions,
        }
        text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        errors: list[str] = []
        for path in self.candidates:
            try:
                self._write_atomic(path, text)
            except OSError as exc:
                errors.append(f"{path}: {type(exc).__name__}: {exc}")
                continue
            if path != self.path:
                log.warning(
                    "cannot write %s; writing the solutions file to %s instead",
                    self.path,
                    path,
                )
                self.path = path
            return
        # Every candidate failed: losing the file is bad, but killing the run
        # loses every later answer as well.
        log.error(
            "cannot write the solutions file anywhere: %s",
            "; ".join(errors),
        )

    @staticmethod
    def _write_atomic(path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f".{path.name}.tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
