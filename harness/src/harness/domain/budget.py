"""Token accounting for the competition budget.

Rules from the regulation:

* the budget is measured in **output** tokens;
* 10 input tokens count as 1 output token;
* reasoning tokens count as output tokens (the API reports them inside
  ``completion_tokens``, so no special handling is needed);
* provider-side prompt caching is ignored: every input token is charged.

The actual LLM calls are made by openJiuwen; this module converts the usage
reported by the SDK into the contest currency.
"""

from __future__ import annotations

from dataclasses import dataclass

INPUT_TOKENS_PER_OUTPUT_TOKEN = 10


def token_cost(input_tokens: int, output_tokens: int) -> int:
    """Cost in output tokens, rounding partial input tokens up."""
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("token counts must be non-negative")
    return output_tokens + (
        input_tokens + INPUT_TOKENS_PER_OUTPUT_TOKEN - 1
    ) // INPUT_TOKENS_PER_OUTPUT_TOKEN


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class TokenLedger:
    limit: int | None = None

    def __post_init__(self) -> None:
        self.input_tokens = 0
        self.output_tokens = 0
        self.spent = 0

    @property
    def remaining(self) -> int | None:
        return None if self.limit is None else max(0, self.limit - self.spent)

    @property
    def exhausted(self) -> bool:
        return self.limit is not None and self.spent >= self.limit

    def charge(self, input_tokens: int, output_tokens: int) -> int:
        cost = token_cost(input_tokens, output_tokens)
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.spent += cost
        if self.limit is not None and self.spent > self.limit:
            raise BudgetExceeded(f"spent {self.spent} > limit {self.limit}")
        return cost
