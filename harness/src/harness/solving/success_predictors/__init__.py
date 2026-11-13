"""Success-probability strategies: online model first, heuristic fallback."""

from __future__ import annotations

from typing import Any

from harness.solving.success_predictors.heuristic import success_probability
from harness.solving.success_predictors.model import predict_success

__all__ = ["estimate_success", "predict_success", "success_probability"]


def estimate_success(features: dict[str, Any]) -> float:
    """Return P(success) from the model, or the heuristic when it is unavailable."""
    probability = predict_success(features)
    if probability is None:
        probability = success_probability(features)
    return max(0.0, min(1.0, float(probability)))
