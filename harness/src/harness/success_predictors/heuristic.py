"""Hand-written fallback estimate of success probability."""

from __future__ import annotations

from typing import Any


def success_probability(features: dict[str, Any]) -> float:
    """Heuristic chance that one more turn produces a usable answer."""
    kind = features.get("answer_kind", "none")
    if kind in {"done", "value"}:
        return 0.0
    probability = 0.50
    if kind == "impossible":
        probability = 0.18
    if features.get("hit_token_limit"):
        probability = min(probability, 0.30)
    if features.get("script_error") or features.get("script_timed_out"):
        probability -= 0.10
    elif features.get("exit_code") not in (0, None):
        probability -= 0.05
    if features.get("reasoning_keyword_impossible"):
        probability = min(probability, 0.22)
    if features.get("reasoning_keyword_give_up"):
        probability = min(probability, 0.20)
    if features.get("reasoning_words", 0) > 300:
        probability += 0.05
    if features.get("script_has_write_answer"):
        probability += 0.05
    if features.get("script_has_python"):
        probability += 0.03
    if features.get("output_chars", 0) > 0:
        probability += 0.03
    if features.get("tests_in_overview"):
        probability += 0.02
    return max(0.02, min(0.92, probability))
