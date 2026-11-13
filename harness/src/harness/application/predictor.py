"""Online success predictor.

The model is trained in research experiment ``0007`` and shipped as a
scikit-learn pipeline.  It runs after the first turn and predicts the
probability that the final answer will be accepted.  Loading is lazy: the
harness must start and solve tasks even if the model file or scikit-learn is
missing.  In that case ``predict_success`` returns ``None`` and the caller
falls back to the hand-written heuristic in ``features.py``.
"""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).with_name("models")
MODEL_PATH = MODEL_DIR / "online_correct_model.joblib"
META_PATH = MODEL_DIR / "online_model.json"

_NUMERIC_DEFAULT = 0.0
_CATEGORICAL_DEFAULT = "none"


@lru_cache(maxsize=1)
def _load() -> tuple[Any, dict[str, Any]] | None:
    if not MODEL_PATH.is_file() or not META_PATH.is_file():
        log.warning("online predictor: model files are missing")
        return None
    try:
        import joblib

        meta = json.loads(META_PATH.read_text(encoding="utf-8"))
        model = joblib.load(MODEL_PATH)
    except Exception:  # noqa: BLE001 - never block task processing
        log.warning("online predictor: cannot load model", exc_info=True)
        return None
    return model, meta


def available() -> bool:
    return _load() is not None


def predict_success(features: dict[str, Any]) -> float | None:
    """Return calibrated P(correct) or ``None`` when the model is unusable.

    ``features`` is the turn-feature dict produced by ``extract_features``.
    Missing optional values default to zero / ``"none"``; the model was trained
    with median imputation, but keeping the row complete avoids surprises.
    """
    loaded = _load()
    if loaded is None:
        return None
    model, meta = loaded
    try:
        import pandas as pd

        row: dict[str, Any] = {}
        for name in meta["numeric_features"]:
            value = features.get(name, _NUMERIC_DEFAULT)
            try:
                row[name] = float(value) if value is not None else _NUMERIC_DEFAULT
            except (TypeError, ValueError):
                row[name] = _NUMERIC_DEFAULT
        for name in meta["categorical_features"]:
            value = features.get(name, _CATEGORICAL_DEFAULT)
            row[name] = str(value) if value not in (None, "") else _CATEGORICAL_DEFAULT
        columns = meta["numeric_features"] + meta["categorical_features"]
        frame = pd.DataFrame([row], columns=columns)
        probability = float(model.predict_proba(frame)[0, 1])
    except Exception:  # noqa: BLE001 - fall back to the heuristic
        log.warning("online predictor: inference failed", exc_info=True)
        return None
    if not 0.0 <= probability <= 1.0:
        return None
    return probability
