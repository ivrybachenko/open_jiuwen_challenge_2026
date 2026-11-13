"""Follow-up wave selection and the success/cost heuristic."""

from __future__ import annotations

from typing import Any

from harness.application.config import Settings
from harness.application.predictor import predict_success
from harness.application.state import TaskState
from harness.application.tasks import Task


def success_probability(features: dict[str, Any]) -> float:
    """Heuristic chance that one more turn produces a usable answer."""
    kind = features.get("answer_kind", "none")
    if kind in {"done", "value"}:
        return 0.0
    probability = 0.50
    if kind == "impossible":
        probability = 0.18
    if features.get("hit_token_limit"):
        probability = min(probability, 0.30)
    if features.get("script_error") or features.get("script_timed_out"):
        probability -= 0.10
    elif features.get("exit_code") not in (0, None):
        probability -= 0.05
    if features.get("reasoning_keyword_impossible"):
        probability = min(probability, 0.22)
    if features.get("reasoning_keyword_give_up"):
        probability = min(probability, 0.20)
    if features.get("reasoning_words", 0) > 300:
        probability += 0.05
    if features.get("script_has_write_answer"):
        probability += 0.05
    if features.get("script_has_python"):
        probability += 0.03
    if features.get("output_chars", 0) > 0:
        probability += 0.03
    if features.get("tests_in_overview"):
        probability += 0.02
    return max(0.02, min(0.92, probability))


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
    probability = predict_success(features)
    if probability is None:
        probability = success_probability(features)
    probability = max(0.0, min(1.0, float(probability)))
    if probability <= 0:
        return 0.0
    cost = estimate_retry_cost(spent_cost, wave2_max_tokens)
    return probability * float(reward) / max(1, cost)


class FollowUpSelector:
    """Pick unfinished tasks worth another wave."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def select(
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

    def select_wave2(
        self,
        tasks: list[Task],
        states: dict[str, TaskState],
        *,
        remaining: int | None = None,
    ) -> list[tuple[Task, TaskState]]:
        """Compatibility wrapper for the second wave."""
        return self.select(tasks, states, 2, remaining=remaining)
