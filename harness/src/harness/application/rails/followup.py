"""Follow-up wave preparation rail.

The rail owns both the user-facing warning text and the state transition that
starts the next wave.
"""

from __future__ import annotations

from openjiuwen.core.single_agent.rail.base import (
    AgentCallbackContext,
    AgentRail,
)

from harness.application.state import TaskState


def followup_warning(state: TaskState, *, final: bool) -> str:
    """Build the user message that starts a follow-up wave."""
    lines = ["The previous attempt did not produce a usable final answer."]
    last = state.turns[-1] if state.turns else {}
    features = last.get("features") or {}
    if last.get("model_error"):
        lines.append("The previous model call failed before producing a script.")
    if state.answer_kind == "impossible":
        lines.append(
            "Your previous answer declared this task IMPOSSIBLE. Re-check that "
            "conclusion; if a reasonable approach exists, try it. If it is "
            "still impossible, write IMPOSSIBLE again."
        )
    elif features.get("script_mentions_impossible") or features.get(
        "reasoning_keyword_impossible"
    ):
        lines.append(
            "Your previous reply suggested that the task might be impossible. "
            "Either solve it or write IMPOSSIBLE to answer.txt."
        )
    if features.get("hit_token_limit"):
        lines.append("The previous reply was cut off before it was complete.")
    if last.get("script_timed_out"):
        lines.append("The previous script timed out.")
    elif last.get("script_error"):
        lines.append("The previous script could not be started.")
    elif last.get("exit_code") not in (0, None):
        lines.append(
            f"The previous script exited with code {last.get('exit_code')}."
        )
    if not last.get("answer"):
        lines.append(
            "The previous script did not create a non-empty answer.txt."
        )
        lines.append(
            "Even if the tests already pass, this turn must end by writing "
            "answer.txt (DONE for coding tasks)."
        )
    lines.append(
        "Continue from the current workspace state. Reply with one bash "
        "script and nothing else."
    )
    if final:
        lines.append(
            "This is the final attempt: combine every remaining command into "
            "one script and write answer.txt at the end. Do not spend it on a "
            "single grep, ls or cat."
        )
    return "\n".join(lines)


class FollowUpRail(AgentRail):
    """Prepare the conversation before a follow-up wave."""

    priority = 90

    async def before_invoke(self, ctx: AgentCallbackContext) -> None:
        wave = int(ctx.extra.get("wave", 1) or 1)
        if wave <= 1:
            return
        task = ctx.extra.get("task")
        state = ctx.extra.get("state")
        if task is None or state is None or state.wave_done(wave):
            return
        state.selected_wave2 = True
        store = ctx.agent.state_store
        store.clear_answers(task)
        warning = followup_warning(
            state, final=wave >= ctx.agent.settings.max_waves
        )
        state.messages.append({"role": "user", "content": warning})
        store.save(task, state)
