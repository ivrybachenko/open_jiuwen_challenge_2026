"""JSON/console reporting helpers."""

from __future__ import annotations

import json
from pathlib import Path


def write_json(path: str | Path, payload: dict) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def tail(text: str | None, limit: int = 4000) -> str:
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return "..." + text[-limit:]


def format_seconds(seconds: float | None) -> str:
    if seconds is None:
        return "n/a"
    seconds = max(0.0, float(seconds))
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, rest = divmod(int(round(seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {rest}s"
    return f"{minutes}m {rest}s"


def format_size(size_bytes: int | None) -> str:
    if size_bytes is None:
        return "n/a"
    value = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1000.0 or unit == "TB":
            return f"{value:.2f} {unit}"
        value /= 1000.0
    return f"{value:.2f} TB"


def format_tokens(input_tokens: int, output_tokens: int, cost: int) -> str:
    return f"{input_tokens} in, {output_tokens} out, cost {cost}"
