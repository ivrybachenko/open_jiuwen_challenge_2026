"""Append-only attempt journal (JSONL plus readable YAML)."""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

ATTEMPTS_FILE = "bash_attempts.jsonl"
READABLE_DIR = "readable"


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


def _safe_stem(value: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "unknown")).strip("._-")
    return stem or "unknown"
