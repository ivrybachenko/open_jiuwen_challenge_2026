"""Wave scheduling: pick unfinished tasks for the next round."""

from __future__ import annotations

from typing import Any

from harness.config import Settings
from harness.solving.success_predictors import estimate_success
from harness.tasks import Task, TaskState


def order_tasks_for_wave1(tasks: list[Task]) -> list[Task]:
    """Order wave 1 by decreasing reward, then by task id.

    The expected cost before the first turn is not used: the a-priori cost
    forecast was weak (experiment 0006), while ``reward`` is always available.
    """
    return sorted(tasks, key=lambda task: (-task.reward, task.task_id))


def estimate_retry_cost(spent_cost: int, turns: int = 1) -> int:
    """Estimate one more turn from the average cost of completed turns.

    A retry usually repeats the previous context and adds output of a similar
    size, so the next turn costs roughly the average turn cost with a small
    growth factor.  The old ``spent * 1.1 + wave2_max_tokens`` formula
    reserved a full 4000-token reply and blocked retries that actually cost a
    few hundred tokens (experiment 0015).
    """
    completed = max(1, int(turns))
    average = max(0, int(spent_cost)) / completed
    return max(300, int(average * 1.2))


def promise_score(
    *,
    reward: float,
    features: dict[str, Any],
    spent_cost: int,
    turns: int = 1,
) -> float:
    probability = estimate_success(features)
    probability = max(0.0, min(1.0, float(probability)))
    if probability <= 0:
        return 0.0
    cost = estimate_retry_cost(spent_cost, turns)
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
            turns = len(state.turns)
            promise = promise_score(
                reward=task.reward,
                features=last_features,
                spent_cost=state.cost,
                turns=turns,
            )
            state.promise = round(promise, 8)
            if promise <= 0:
                continue
            if remaining is not None:
                estimated = estimate_retry_cost(state.cost, turns)
                if estimated > remaining:
                    continue
            candidates.append((promise, task, state))

        candidates.sort(
            key=lambda item: (-item[0], -item[1].reward, item[1].task_id)
        )
        if self.settings.wave2_max_tasks > 0:
            candidates = candidates[: self.settings.wave2_max_tasks]
        return [(task, state) for _, task, state in candidates]
