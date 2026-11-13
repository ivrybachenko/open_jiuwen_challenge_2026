"""Online success predictor.

The global model is trained in research experiment ``0007``; the per-wave
models (2, 3, 4) are trained in experiment ``0012``.  Both are shipped as
scikit-learn pipelines.  The predictor runs after a turn and returns the
probability that the final answer will be accepted.  Loading is lazy: the
harness must start and solve tasks even if the model files or scikit-learn are
missing.  In that case ``predict_success`` returns ``None`` and
``estimate_success`` falls back to ``heuristic.success_probability``.

``HARNESS_WAVE_MODELS=0`` disables the per-wave models and uses the global
model for every wave.
"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).with_name("models")
MODEL_PATH = MODEL_DIR / "online_correct_model.joblib"
META_PATH = MODEL_DIR / "online_model.json"
WAVE_MODEL_PATH = MODEL_DIR / "wave_models.joblib"
WAVE_META_PATH = MODEL_DIR / "wave_model.json"

_DISABLED = {"0", "false", "off", "no"}

_NUMERIC_DEFAULT = 0.0
_CATEGORICAL_DEFAULT = "none"


def _numeric_value(features: dict[str, Any], name: str) -> float:
    """Adapt the turn-feature dict to the numeric schema used in training.

    ``extract_features`` calls the timeout flag ``script_timed_out`` and keeps
    the error as a string, while the training dataset (experiment 0007) used
    ``timed_out`` and the length of ``script_error``.  Without this adapter
    both model inputs are always zero.
    """
    if name == "timed_out":
        value = features.get("timed_out", features.get("script_timed_out", 0.0))
    elif name == "script_error":
        value = features.get("script_error", 0.0)
        if isinstance(value, str):
            value = len(value)
    else:
        value = features.get(name, _NUMERIC_DEFAULT)
    try:
        return float(value) if value is not None else _NUMERIC_DEFAULT
    except (TypeError, ValueError):
        return _NUMERIC_DEFAULT


def _feature_frame(features: dict[str, Any], meta: dict[str, Any]):
    """Build the one-row frame expected by a shipped model."""
    import pandas as pd

    row: dict[str, Any] = {}
    for name in meta["numeric_features"]:
        row[name] = _numeric_value(features, name)
    for name in meta["categorical_features"]:
        value = features.get(name, _CATEGORICAL_DEFAULT)
        row[name] = (
            str(value) if value not in (None, "") else _CATEGORICAL_DEFAULT
        )
    return pd.DataFrame(
        [row],
        columns=meta["numeric_features"] + meta["categorical_features"],
    )


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


@lru_cache(maxsize=1)
def _load_wave_models() -> tuple[dict[str, Any], dict[str, Any]] | None:
    """Load the optional per-wave models and their metadata."""
    if not WAVE_MODEL_PATH.is_file() or not WAVE_META_PATH.is_file():
        return None
    try:
        import joblib

        meta = json.loads(WAVE_META_PATH.read_text(encoding="utf-8"))
        models = joblib.load(WAVE_MODEL_PATH)
    except Exception:  # noqa: BLE001 - never block task processing
        log.warning("wave predictor: cannot load models", exc_info=True)
        return None
    if not isinstance(models, dict) or not models:
        return None
    return models, meta


def _wave_models_enabled() -> bool:
    """``HARNESS_WAVE_MODELS=0`` restores the single-model behaviour."""
    return os.environ.get("HARNESS_WAVE_MODELS", "1").strip().lower() not in _DISABLED


def available() -> bool:
    return _load() is not None or _load_wave_models() is not None


def available_wave(wave: int) -> bool:
    """True when a wave-specific model is loaded for this wave."""
    loaded = _load_wave_models()
    if loaded is None:
        return False
    models, _ = loaded
    if wave >= 5:
        return "4" in models
    return str(wave) in models


def _loaded_for_wave(
    wave: int,
) -> tuple[Any, dict[str, Any], str] | None:
    """Return the model, metadata and source for a turn on ``wave``.

    Wave 1 always uses the global model.  Waves 2-4 use their own model when
    present.  Waves 5+ reuse the wave-4 model: the pilot has only 21 wave-5
    rows, but its calibrated probabilities were much closer to the observed
    rate than the global model's.
    """
    if _wave_models_enabled():
        loaded = _load_wave_models()
        if loaded is not None:
            models, meta = loaded
            key = "4" if wave >= 5 else str(wave)
            model = models.get(key)
            if model is not None:
                return model, meta, f"wave{key}"
    loaded = _load()
    if loaded is None:
        return None
    model, meta = loaded
    return model, meta, "global"


def _predict(model: Any, meta: dict[str, Any], features: dict[str, Any]) -> float | None:
    try:
        frame = _feature_frame(features, meta)
        probability = float(model.predict_proba(frame)[0, 1])
    except Exception:  # noqa: BLE001 - caller decides on the fallback
        log.debug("success predictor: inference failed", exc_info=True)
        return None
    if not 0.0 <= probability <= 1.0:
        return None
    return probability


def predict_success(features: dict[str, Any]) -> float | None:
    """Return calibrated P(correct) or ``None`` when every model is unusable.

    ``features`` is the turn-feature dict produced by ``extract_features``.
    The turn's ``wave`` selects a per-wave model; missing artifacts fall back
    to the global model, and the caller falls back to the heuristic.
    """
    try:
        wave = int(features.get("wave", 1) or 1)
    except (TypeError, ValueError):
        wave = 1
    loaded = _loaded_for_wave(wave)
    if loaded is None:
        return None
    model, meta, source = loaded
    probability = _predict(model, meta, features)
    if probability is not None:
        return probability
    # A broken wave model must not disable the global one.
    if source != "global":
        global_loaded = _load()
        if global_loaded is not None:
            return _predict(*global_loaded, features)
    return None
