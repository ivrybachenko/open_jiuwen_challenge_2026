"""Budget accounting rail.

The rail adds no prompt text and makes no model calls: it only reads the
response usage and updates the per-task state and the run ledger.
"""

from __future__ import annotations

import logging

from openjiuwen.core.single_agent.rail.base import (
    AgentCallbackContext,
    AgentRail,
)

from harness.application.llm import BudgetExceeded, TokenLedger, token_cost

log = logging.getLogger(__name__)


class BudgetRail(AgentRail):
    """Charge the contest ledger after every model call."""

    priority = 95

    def __init__(self, ledger: TokenLedger) -> None:
        self.ledger = ledger
        self.budget_exceeded = False

    async def after_model_call(self, ctx: AgentCallbackContext) -> None:
        reply = getattr(ctx.inputs, "response", None)
        state = ctx.extra.get("state")
        if reply is None or state is None:
            return
        input_tokens = int(getattr(reply, "input_tokens", 0) or 0)
        output_tokens = int(getattr(reply, "output_tokens", 0) or 0)
        state.input_tokens += input_tokens
        state.output_tokens += output_tokens
        state.cost += token_cost(input_tokens, output_tokens)
        try:
            self.ledger.charge(input_tokens, output_tokens)
        except BudgetExceeded:
            self.budget_exceeded = True
            log.warning("token budget exceeded after %s", state.task_id)
