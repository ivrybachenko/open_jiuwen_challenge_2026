#!/usr/bin/env python3
"""Ask the allowed chat model to estimate task cost before solving.

This is a baseline for the static predictor, not a trained model.  The probe
costs one extra LLM call per task, so its own tokens must be counted against
the value it adds.

Usage::

    LLM_API_KEY="$NEURAL_DEEP_API_KEY" harness/.venv/bin/python \
        research/experiments/0009-llm-cost-probe/llm_probe.py \
        --dataset research/experiments/0009-llm-cost-probe/results/probe_tasks.jsonl \
        --limit 80 --out research/experiments/0009-llm-cost-probe/results/probe_raw.jsonl
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.neuraldeep.ru/v1")

PROMPT = """You are estimating the cost of a task before a coding agent tries it.

The agent can make at most two turns. In each turn it writes one complete bash
script; the harness executes it and returns the output. The agent pays output
tokens in full and input tokens at one tenth. A typical turn costs a few
hundred tokens.

Task overview (exactly what the agent sees before its first turn):

{overview}

Estimate, before any attempt:
1. total tokens the agent will spend on this task over both turns;
2. whether it will need a second turn;
3. whether the task is solvable as stated;
4. a coarse cost bucket.

Return only one JSON object, no markdown and no explanation:
{{"tokens": <integer>, "needs_second_turn": <0 or 1>, "solvable": <0 or 1>, "bucket": "low" | "medium" | "high", "confidence": <number between 0 and 1>}}
"""


def _parse_json(text: str) -> dict[str, Any] | None:
    text = (text or "").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--model", default="qwen3.6-35b-a3b-noreason")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--max-tokens", type=int, default=160)
    parser.add_argument("--sleep", type=float, default=0.5)
    args = parser.parse_args(argv)

    key = os.environ.get("LLM_API_KEY") or os.environ.get("NEURAL_DEEP_API_KEY")
    if not key:
        raise SystemExit("LLM_API_KEY or NEURAL_DEEP_API_KEY must be set")
    from openai import OpenAI

    client = OpenAI(api_key=key, base_url=BASE_URL, timeout=180.0)
    rows = [json.loads(line) for line in args.dataset.read_text(
        encoding="utf-8").splitlines() if line.strip()]
    if args.limit:
        rows = rows[: args.limit]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for index, row in enumerate(rows, start=1):
            prompt = PROMPT.format(overview=row.get("overview", "")[:8000])
            reply = None
            error = ""
            usage = None
            for attempt in range(6):
                try:
                    response = client.chat.completions.create(
                        model=args.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.0,
                        max_tokens=args.max_tokens,
                    )
                    reply = response.choices[0].message.content or ""
                    usage = response.usage
                    break
                except Exception as exc:  # noqa: BLE001
                    error = f"{type(exc).__name__}: {exc}"
                    if "429" in error or "rate" in error.lower():
                        time.sleep(30 + attempt * 15)
                    else:
                        time.sleep(5)
            parsed = _parse_json(reply or "")
            record = {
                "task_id": row["task_id"],
                "rel": row["rel"],
                "task_type": row["task_type"],
                "reward": row.get("reward", ""),
                "reply": reply,
                "parsed": parsed,
                "error": error,
                "input_tokens": getattr(usage, "prompt_tokens", 0),
                "output_tokens": getattr(usage, "completion_tokens", 0),
            }
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            fh.flush()
            print(f"{index}/{len(rows)} {row['task_id']} -> {parsed}",
                  file=sys.stderr)
            time.sleep(args.sleep)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
