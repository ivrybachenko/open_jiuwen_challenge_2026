"""Follow-up wave preparation rail."""

from __future__ import annotations

from openjiuwen.core.single_agent.rail.base import (
    AgentCallbackContext,
    AgentRail,
)


class FollowUpRail(AgentRail):
    """Prepare the conversation before a follow-up wave.

    The agent owns the warning text and the stale-answer cleanup; the rail only
    invokes that step on the openJiuwen before-invoke lifecycle.
    """

    priority = 90

    async def before_invoke(self, ctx: AgentCallbackContext) -> None:
        wave = int(ctx.extra.get("wave", 1) or 1)
        if wave <= 1:
            return
        task = ctx.extra.get("task")
        state = ctx.extra.get("state")
        if task is None or state is None:
            return
        ctx.agent.prepare_followup(task, state, wave)
