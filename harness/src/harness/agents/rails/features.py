"""Per-turn feature capture rail."""

from __future__ import annotations

from openjiuwen.core.single_agent.rail.base import (
    AgentCallbackContext,
    AgentRail,
)

from harness.attempts import extract_features


class FeatureRail(AgentRail):
    """Fill the per-turn feature record used by the success predictor."""

    priority = 70

    async def after_invoke(self, ctx: AgentCallbackContext) -> None:
        turn = ctx.extra.get("turn")
        task = ctx.extra.get("task")
        state = ctx.extra.get("state")
        reply = ctx.extra.get("reply")
        execution = ctx.extra.get("execution")
        answer_info = ctx.extra.get("answer_info")
        if (
            turn is None
            or task is None
            or state is None
            or reply is None
            or execution is None
            or answer_info is None
        ):
            return
        script = str(ctx.extra.get("script", "") or "")
        turn["features"] = extract_features(
            task_type=task.task_type,
            reward=task.reward,
            wave=int(ctx.extra.get("wave", 1) or 1),
            turn=int(turn.get("turn", 1) or 1),
            reasoning=str(getattr(reply, "reasoning", "") or ""),
            model_duration_seconds=float(
                getattr(reply, "duration_seconds", 0.0) or 0.0
            ),
            input_tokens=int(getattr(reply, "input_tokens", 0) or 0),
            output_tokens=int(getattr(reply, "output_tokens", 0) or 0),
            reasoning_tokens=int(getattr(reply, "reasoning_tokens", 0) or 0),
            finish_reason=str(getattr(reply, "finish_reason", "") or ""),
            max_tokens=int(ctx.extra.get("max_tokens", 0) or 0),
            script=script,
            exit_code=execution.exit_code,
            script_duration_seconds=execution.duration_seconds,
            script_timed_out=execution.timed_out,
            script_error=execution.error,
            output_chars=len(execution.output),
            answer=answer_info,
            tests_in_overview="$ tests" in state.overview,
            output_lines=(
                execution.output.count("\n") + (1 if execution.output else 0)
            ),
            overview_chars=len(state.overview),
            overview_lines=(
                state.overview.count("\n") + (1 if state.overview else 0)
            ),
        )
