"""Model failure rail.

The agent catches provider exceptions and returns ``ModelReply(error=...)``,
so this rail inspects the response instead of relying on an exception hook.
"""

from __future__ import annotations

import logging

from openjiuwen.core.single_agent.rail.base import (
    AgentCallbackContext,
    AgentRail,
)

log = logging.getLogger(__name__)


class FailureRail(AgentRail):
    """Stop the run after three consecutive failed model calls."""

    priority = 96

    def __init__(self) -> None:
        self.failures = 0
        self.abort_requested = False

    async def after_model_call(self, ctx: AgentCallbackContext) -> None:
        reply = getattr(ctx.inputs, "response", None)
        if reply is None:
            return
        # A missing configuration is a harness bug, not a provider outage; the
        # old code did not count it either.
        if (
            getattr(ctx.agent, "_model", None) is None
            and getattr(ctx.agent, "_wave2_model", None) is None
        ):
            return
        error = str(getattr(reply, "error", "") or "")
        if error:
            self.failures += 1
            if self.failures >= 3:
                self.abort_requested = True
            log.warning(
                "model call failed (%d in a row): %s", self.failures, error
            )
        else:
            self.failures = 0
