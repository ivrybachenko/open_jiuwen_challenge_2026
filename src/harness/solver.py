"""Solver interface.

The real planning/execution strategy goes here. ``StubSolver`` is a
placeholder that solves nothing -- replace it with the actual harness.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .config import Settings
from .llm import TokenLedger
from .tasks import Task


@dataclass
class SolveResult:
    answer: str | None = None
    solved: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    note: str = ""


class Solver(ABC):
    name = "base"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.ledger = TokenLedger(settings.budget)

    @property
    def spent(self) -> int:
        return self.ledger.spent

    @abstractmethod
    def solve(self, task: Task) -> SolveResult:
        """Solve one task. Must not write the solutions file itself."""


class StubSolver(Solver):
    """Placeholder: reports every task as unsolved."""

    name = "stub"

    def solve(self, task: Task) -> SolveResult:
        return SolveResult(note="solver strategy not implemented yet")


def build_solver(settings: Settings) -> Solver:
    return StubSolver(settings)
