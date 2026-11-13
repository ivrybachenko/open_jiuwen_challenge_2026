"""Answer submission rail."""

from __future__ import annotations

import logging

from openjiuwen.core.single_agent.rail.base import (
    AgentCallbackContext,
    AgentRail,
)

log = logging.getLogger(__name__)


class AnswerRail(AgentRail):
    """Record the submitted answer and restore it when a retry improves nothing."""

    priority = 80

    async def after_invoke(self, ctx: AgentCallbackContext) -> None:
        task = ctx.extra.get("task")
        state = ctx.extra.get("state")
        answer_info = ctx.extra.get("answer_info")
        wave = int(ctx.extra.get("wave", 1) or 1)
        if task is None or state is None or answer_info is None:
            return
        if answer_info.kind == "impossible":
            state.impossible_declared = True
        if answer_info.text is not None:
            state.answer = answer_info.text
            state.answer_kind = answer_info.kind
        if wave > 1 and answer_info.text is None and state.answer is not None:
            # The retry did not improve on the previous answer; restore it.
            try:
                task.write_answer(state.answer)
            except OSError:
                log.debug(
                    "cannot restore answer for %s", task.task_id, exc_info=True
                )
