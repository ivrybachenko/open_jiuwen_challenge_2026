"""Token accounting and a thin client for the jury's LLM proxy.

Budget rules from the regulation:

* the budget is measured in **output** tokens;
* 10 input tokens count as 1 output token;
* reasoning tokens count as output tokens (the API reports them inside
  ``completion_tokens``, so no special handling is needed);
* provider-side prompt caching is ignored: every input token is charged.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

log = logging.getLogger(__name__)

MODELS = (
    "qwen3.8-27b",
    "qwen3.8-27b-noreason",
    "qwen3.6-35b-a3b",
    "qwen3.6-35b-a3b-noreason",
)
DEFAULT_MODEL = "qwen3.6-35b-a3b"

INPUT_TOKENS_PER_OUTPUT_TOKEN = 10


def token_cost(input_tokens: int, output_tokens: int) -> int:
    """Cost in output tokens, rounding partial input tokens up."""
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("token counts must be non-negative")
    return output_tokens + (input_tokens + INPUT_TOKENS_PER_OUTPUT_TOKEN - 1) // (
        INPUT_TOKENS_PER_OUTPUT_TOKEN
    )


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


class LLMClient:
    """OpenAI-compatible chat client that bills every call to a ledger."""

    def __init__(
        self,
        base_url: str | None,
        api_key: str | None,
        ledger: TokenLedger,
        model: str = DEFAULT_MODEL,
        timeout: float = 120.0,
    ) -> None:
        if not base_url or not api_key:
            raise RuntimeError("LLM_BASE_URL and LLM_API_KEY must be set")
        if model not in MODELS:
            raise ValueError(f"unsupported model: {model}")
        self.model = model
        self.ledger = ledger
        self._timeout = timeout
        self._base_url = base_url
        self._api_key = api_key
        self._client = None

    def chat(self, messages: list[dict], *, model: str | None = None, **kwargs) -> str:
        model = model or self.model
        if model not in MODELS:
            raise ValueError(f"unsupported model: {model}")
        if self.ledger.exhausted:
            raise BudgetExceeded("no budget left")

        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(
                base_url=self._base_url,
                api_key=self._api_key,
                timeout=self._timeout,
            )

        response = self._client.chat.completions.create(
            model=model, messages=messages, **kwargs
        )
        usage = response.usage
        if usage is not None:
            self.ledger.charge(
                input_tokens=usage.prompt_tokens or 0,
                output_tokens=usage.completion_tokens or 0,
            )
        content = response.choices[0].message.content if response.choices else None
        return content or ""
