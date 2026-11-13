"""Wave scheduling: pick unfinished tasks for the next round."""

from __future__ import annotations

from typing import Any

from harness.config import Settings
from harness.solving.success_predictors import estimate_success
from harness.tasks import Task, TaskState


def estimate_retry_cost(spent_cost: int, wave2_max_tokens: int) -> int:
    """Rough cost of one more turn, including the repeated context."""
    return max(500, int(max(0, spent_cost) * 1.10) + int(wave2_max_tokens))


def promise_score(
    *,
    reward: float,
    features: dict[str, Any],
    spent_cost: int,
    wave2_max_tokens: int,
) -> float:
    probability = estimate_success(features)
    probability = max(0.0, min(1.0, float(probability)))
    if probability <= 0:
        return 0.0
    cost = estimate_retry_cost(spent_cost, wave2_max_tokens)
    return probability * float(reward) / max(1, cost)


class WaveScheduler:
    """Pick unfinished tasks worth another wave."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def select_candidates(
        self,
        tasks: list[Task],
        states: dict[str, TaskState],
        wave: int,
        *,
        remaining: int | None = None,
    ) -> list[tuple[Task, TaskState]]:
        candidates: list[tuple[float, Task, TaskState]] = []
        for task in tasks:
            state = states.get(task.task_id)
            if state is None or state.wave_done(wave):
                continue
            if state.answer_kind in {"done", "value"}:
                continue
            last_features = (
                state.turns[-1].get("features") if state.turns else {}
            ) or {}
            promise = promise_score(
                reward=task.reward,
                features=last_features,
                spent_cost=state.cost,
                wave2_max_tokens=self.settings.wave2_max_tokens,
            )
            state.promise = round(promise, 8)
            if promise <= 0:
                continue
            if remaining is not None:
                estimated = estimate_retry_cost(
                    state.cost, self.settings.wave2_max_tokens
                )
                if estimated > remaining:
                    continue
            candidates.append((promise, task, state))

        candidates.sort(
            key=lambda item: (-item[0], -item[1].reward, item[1].task_id)
        )
        if self.settings.wave2_max_tasks > 0:
            candidates = candidates[: self.settings.wave2_max_tasks]
        return [(task, state) for _, task, state in candidates]
