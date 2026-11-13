"""Token accounting used by the evaluators.

This is a copy of ``harness.accounting.budget.token_cost``.  The evaluation
package deliberately does not import the harness package: the evaluator may run
with a different interpreter (for example the system Python) while the harness
runs from ``harness/.venv``.  Keep the formula in sync with the harness:

    cost = output_tokens + ceil(input_tokens / 10)
"""

from __future__ import annotations

INPUT_TOKENS_PER_OUTPUT_TOKEN = 10


def token_cost(input_tokens: int, output_tokens: int) -> int:
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("token counts must be non-negative")
    return output_tokens + (
        input_tokens + INPUT_TOKENS_PER_OUTPUT_TOKEN - 1
    ) // INPUT_TOKENS_PER_OUTPUT_TOKEN
