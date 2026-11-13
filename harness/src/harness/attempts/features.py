"""Per-turn features used by the success predictor and wave policy."""

from __future__ import annotations

import math
import re
from typing import Any

from harness.answers.model import AnswerInfo

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

# Counts used by the online success predictor (experiment 0007).  They are
# intentionally simple and cheap: one regex pass over the script per pattern.
SCRIPT_COUNT_PATTERNS = {
    "n_cat": re.compile(r"\bcat\b"),
    "n_grep": re.compile(r"\bgrep\b"),
    "n_find": re.compile(r"\bfind\b"),
    "n_ls": re.compile(r"\bls\b"),
    "n_head": re.compile(r"\bhead\b"),
    "n_tail": re.compile(r"\btail\b"),
    "n_awk": re.compile(r"\bawk\b"),
    "n_sed": re.compile(r"\bsed\b"),
    "n_sort": re.compile(r"\bsort\b"),
    "n_wc": re.compile(r"\bwc\b"),
    "n_python": re.compile(r"\bpython3?\b"),
    "n_test": re.compile(r"\b(?:pytest|unittest|test_)\b"),
    "n_for": re.compile(r"\bfor\b"),
    "n_while": re.compile(r"\bwhile\b"),
    "n_if": re.compile(r"\bif\b"),
    "n_pipe": re.compile(r"\|"),
    "n_semicolon": re.compile(r";"),
    "n_redirect": re.compile(r">"),
    "n_echo": re.compile(r"\becho\b"),
    "n_impossible": re.compile(r"(?i)\bimpossible\b"),
}


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
    output_lines: int = 0,
    overview_chars: int = 0,
    overview_lines: int = 0,
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
        "cost": int(output_tokens) + math.ceil(max(0, int(input_tokens)) / 10),
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
        "output_lines": int(output_lines),
        "overview_chars": int(overview_chars),
        "overview_lines": int(overview_lines),
        "script_words": len(script.split()),
        "answer_present": answer.present,
        "answer_impossible": answer.kind == "impossible",
        "exit_bad": exit_code not in (0, None),
        **{name: _count(pattern, script)
           for name, pattern in SCRIPT_COUNT_PATTERNS.items()},
        "answer_kind": answer.kind,
        "answer_chars": len(answer.text or ""),
        "answer_first_line": answer.first_line,
        "tests_in_overview": bool(tests_in_overview),
        **{f"reasoning_keyword_{key}": value for key, value in keywords.items()},
    }


def _safe_stem(value: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "unknown")).strip("._-")
    return stem or "unknown"
