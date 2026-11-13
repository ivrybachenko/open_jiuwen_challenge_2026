#!/usr/bin/env python3
"""Run the harness with exponential backoff on proxy 429 responses.

The proxy key has a hard concurrent/rate limit.  The stock harness treats a
failed model call as a failed turn and aborts after three failures in a row,
which loses all later tasks.  For data collection we wrap ``_call_model``:
on a 429 it sleeps, resets the failure counter and retries instead of
recording a failed turn.  All other behavior is unchanged.

This file is a *research* wrapper; the shipped harness is not modified.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT / "harness" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "harness" / "src"))

from harness.application.solver import BashAgentSolver, ModelReply  # noqa: E402

_ORIGINAL = BashAgentSolver._call_model


def _is_rate_limit(error: str) -> bool:
    text = (error or "").lower()
    return "429" in text or "rate limit" in text or "ratelimit" in text


async def _call_model_with_backoff(self, messages, *, max_tokens):
    delay = 15.0
    last: ModelReply | None = None
    for attempt in range(8):
        reply = await _ORIGINAL(self, messages, max_tokens=max_tokens)
        last = reply
        if not reply.error or not _is_rate_limit(reply.error):
            return reply
        # The stock method counted this as a consecutive failure; undo that.
        self._model_failures = 0
        self._abort_requested = False
        await asyncio.sleep(delay)
        delay = min(90.0, delay * 1.6)
    return last or ModelReply(error="rate limit retries exhausted")


BashAgentSolver._call_model = _call_model_with_backoff

from harness.application.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
