"""Turn features for the future difficulty predictor.

The harness v0002 does not train a model yet.  It records the same signals the
predictor will need -- reasoning, usage, script shape, execution result and the
submitted answer -- and ranks wave-2 candidates with a transparent heuristic.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

ATTEMPTS_FILE = "bash_attempts.jsonl"
READABLE_DIR = "readable"

IMPOSSIBLE_PATTERN = re.compile(
    r"\b(impossible|unsolvable|no\s+solution|cannot\s+be\s+solved|"
    r"not\s+solvable|contradict|inconsistent|insufficient\s+information|"
    r"ambiguous|cannot\s+determine|not\s+enough\s+information)\b",
    re.IGNORECASE,
)
GIVE_UP_PATTERN = re.compile(
    r"\b(give\s+up|surrender|abort|exit|skip)\b", re.IGNORECASE
)
FILE_OP_PATTERN = re.compile(
    r"\b(cat|ls|find|grep|head|tail|awk|sed|cut|sort|uniq|wc)\b"
)
PYTHON_PATTERN = re.compile(r"\b(python3?|pytest|unittest)\b")
WRITE_PATTERN = re.compile(
    r"(answer\.txt|>\s*answer|tee\s+answer|write_text|open\s*\([^)]*answer)",
    re.IGNORECASE,
)
TEST_PATTERN = re.compile(r"\b(pytest|unittest|test_[A-Za-z0-9_]+\.py)\b")


@dataclass(frozen=True)
class AnswerInfo:
    text: str | None
    kind: str
    first_line: str = ""

    @property
    def present(self) -> bool:
        return self.text is not None


def classify_answer(text: str | None) -> AnswerInfo:
    if text is None or not text.strip():
        return AnswerInfo(text=None, kind="none")
    stripped = text.strip()
    first_line = stripped.splitlines()[0].strip()
    if first_line.upper().startswith("IMPOSSIBLE"):
        return AnswerInfo(text=stripped, kind="impossible", first_line=first_line)
    if stripped.upper() in {"DONE", "OK", "SUCCESS", "PASS", "TESTS PASS"}:
        return AnswerInfo(text=stripped, kind="done", first_line=first_line)
    return AnswerInfo(text=stripped, kind="value", first_line=first_line)


def _count(pattern: re.Pattern[str], text: str) -> int:
    return len(pattern.findall(text or ""))


def extract_features(
    *,
    task_type: str,
    reward: float,
    wave: int,
    turn: int,
    reasoning: str,
    model_duration_seconds: float,
    input_tokens: int,
    output_tokens: int,
    reasoning_tokens: int,
    finish_reason: str,
    max_tokens: int,
    script: str,
    exit_code: int | None,
    script_duration_seconds: float,
    script_timed_out: bool,
    script_error: str,
    output_chars: int,
    answer: AnswerInfo,
    tests_in_overview: bool,
) -> dict[str, Any]:
    reasoning = reasoning or ""
    script = script or ""
    words = reasoning.split()
    hit_limit = (
        finish_reason == "length"
        or (max_tokens > 0 and output_tokens >= max_tokens)
    )
    keywords = {
        "impossible": _count(IMPOSSIBLE_PATTERN, reasoning),
        "give_up": _count(GIVE_UP_PATTERN, reasoning),
        "file_ops": _count(FILE_OP_PATTERN, reasoning),
        "python": _count(PYTHON_PATTERN, reasoning),
        "write_answer": _count(WRITE_PATTERN, reasoning),
        "tests": _count(TEST_PATTERN, reasoning),
    }
    return {
        "task_type": task_type,
        "reward": float(reward),
        "wave": int(wave),
        "turn": int(turn),
        "reasoning_chars": len(reasoning),
        "reasoning_words": len(words),
        "reasoning_lines": reasoning.count("\n") + (1 if reasoning else 0),
        "reasoning_duration_seconds": round(model_duration_seconds, 3),
        "reasoning_tokens": int(reasoning_tokens),
        "input_tokens": int(input_tokens),
        "output_tokens": int(output_tokens),
        "finish_reason": finish_reason,
        "hit_token_limit": bool(hit_limit),
        "script_chars": len(script),
        "script_lines": script.count("\n") + (1 if script else 0),
        "script_has_python": bool(PYTHON_PATTERN.search(script)),
        "script_has_file_ops": bool(FILE_OP_PATTERN.search(script)),
        "script_has_write_answer": bool(WRITE_PATTERN.search(script)),
        "script_has_tests": bool(TEST_PATTERN.search(script)),
        "script_mentions_impossible": bool(IMPOSSIBLE_PATTERN.search(script)),
        "exit_code": exit_code,
        "script_duration_seconds": round(script_duration_seconds, 3),
        "script_timed_out": bool(script_timed_out),
        "script_error": script_error,
        "output_chars": int(output_chars),
        "answer_present": answer.present,
        "answer_kind": answer.kind,
        "answer_chars": len(answer.text or ""),
        "answer_first_line": answer.first_line,
        "tests_in_overview": bool(tests_in_overview),
        **{f"reasoning_keyword_{key}": value for key, value in keywords.items()},
    }


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


def estimate_retry_cost(spent_cost: int, wave2_max_tokens: int) -> int:
    """Rough cost of one more turn, including the repeated context."""
    return max(500, int(max(0, spent_cost) * 1.10) + int(wave2_max_tokens))


def promise_score(
    *,
    reward: float,
    features: dict[str, Any],
    spent_cost: int,
    wave2_max_tokens: int,
) -> float:
    probability = success_probability(features)
    if probability <= 0:
        return 0.0
    cost = estimate_retry_cost(spent_cost, wave2_max_tokens)
    return probability * float(reward) / max(1, cost)


def _safe_stem(value: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "unknown")).strip("._-")
    return stem or "unknown"


class AttemptLogger:
    """Append one JSONL record and one readable YAML view per turn."""

    def __init__(self, directory: Path | None, run_id: str | None = None) -> None:
        self.directory = Path(directory) if directory else None
        self.run_id = run_id

    def log(self, record: dict[str, Any]) -> None:
        if self.directory is None:
            return
        payload = dict(record)
        if self.run_id:
            payload["run_id"] = self.run_id
        payload.setdefault(
            "logged_at", datetime.now(timezone.utc).isoformat()
        )
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            path = self.directory / ATTEMPTS_FILE
            with path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(payload, ensure_ascii=False) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
        except (OSError, TypeError, ValueError):
            log.warning("cannot write attempt log", exc_info=True)
        try:
            self._write_yaml(payload)
        except Exception:  # noqa: BLE001 - JSONL is the source of truth
            log.warning("cannot write readable attempt YAML", exc_info=True)

    def _write_yaml(self, payload: dict[str, Any]) -> None:
        if self.directory is None:
            return
        import yaml

        base = self.directory / READABLE_DIR
        base.mkdir(parents=True, exist_ok=True)
        task_id = _safe_stem(str(payload.get("task_id", "unknown")))
        wave = _safe_stem(str(payload.get("wave", "0")))
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
        path = base / f"{task_id}__wave{wave}__{stamp}.yaml"

        class Dumper(yaml.SafeDumper):
            pass

        def represent_str(dumper: Any, data: str) -> Any:
            style = "|" if "\n" in data else None
            return dumper.represent_scalar(
                "tag:yaml.org,2002:str", data, style=style
            )

        Dumper.add_representer(str, represent_str)
        with path.open("w", encoding="utf-8") as stream:
            yaml.dump(
                payload,
                stream,
                Dumper=Dumper,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False,
                width=100,
            )
