"""Read/write the harness score datasets.

The files are TSV (tab-separated) and are updated atomically.  Existing
space-separated files are accepted and rewritten with tabs.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path

HARNESS_INFO_HEADER = ("harness_version", "parent_harness_version", "description")
TASK_SCORE_HEADER = (
    "harness_version",
    "run_id",
    "task_id",
    "is_solved_correctly",
    "cost_tokens",
    "cost_seconds",
)
TASK_SET_SCORE_HEADER = (
    "harness_version",
    "run_id",
    "task_set_id",
    "score",
    "cost_tokens",
    "cost_seconds",
)

_VERSION_RE = re.compile(r'^\s*version\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)


def current_harness_version(repo_root: str | Path) -> str:
    """Read the version from ``harness/pyproject.toml``."""
    repo_root = Path(repo_root)
    pyproject = repo_root / "harness" / "pyproject.toml"
    try:
        text = pyproject.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot read {pyproject}: {exc}") from exc
    match = _VERSION_RE.search(text)
    if not match:
        raise ValueError(f"no [project].version in {pyproject}")
    return match.group(1)


def resolve_harness_version(
    repo_root: str | Path,
    requested: str | None = None,
) -> str:
    """Return the current version, or fail if ``requested`` does not match."""
    current = current_harness_version(repo_root)
    if requested is None:
        return current
    requested = str(requested).strip()
    if requested != current:
        raise ValueError(
            "harness version mismatch: "
            f"requested {requested!r}, current {current!r}"
        )
    return current


def new_run_id() -> str:
    """Unique run identifier (UTC timestamp with microseconds)."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")


def record_task_score(
    repo_root: str | Path,
    *,
    task_id: str,
    harness_version: str,
    run_id: str,
    is_solved_correctly: bool,
    cost_tokens: int,
    cost_seconds: float,
) -> Path:
    repo_root = Path(repo_root)
    path = (
        repo_root
        / "data"
        / "harness_task_score"
        / f"harness_v_{harness_version}.tsv"
    )
    rows = _read_rows(path, TASK_SCORE_HEADER)
    _upsert(
        rows,
        ("harness_version", "run_id", "task_id"),
        {
            "harness_version": harness_version,
            "run_id": run_id,
            "task_id": task_id,
            "is_solved_correctly": _format_bool(is_solved_correctly),
            "cost_tokens": str(int(cost_tokens)),
            "cost_seconds": _format_seconds(cost_seconds),
        },
    )
    rows.sort(
        key=lambda row: (
            row["harness_version"],
            row["task_id"],
            row["run_id"],
        )
    )
    _write_rows(path, TASK_SCORE_HEADER, rows)
    return path


def record_task_set_score(
    repo_root: str | Path,
    *,
    task_set_id: str,
    harness_version: str,
    run_id: str,
    score: float,
    cost_tokens: int,
    cost_seconds: float,
) -> Path:
    repo_root = Path(repo_root)
    path = (
        repo_root
        / "data"
        / "harness_task_set_score"
        / f"harness_v_{harness_version}.tsv"
    )
    rows = _read_rows(path, TASK_SET_SCORE_HEADER)
    _upsert(
        rows,
        ("harness_version", "run_id", "task_set_id"),
        {
            "harness_version": harness_version,
            "run_id": run_id,
            "task_set_id": task_set_id,
            "score": _format_score(score),
            "cost_tokens": str(int(cost_tokens)),
            "cost_seconds": _format_seconds(cost_seconds),
        },
    )
    rows.sort(
        key=lambda row: (
            row["harness_version"],
            row["task_set_id"],
            row["run_id"],
        )
    )
    _write_rows(path, TASK_SET_SCORE_HEADER, rows)
    return path


def clear_task_scores(
    repo_root: str | Path,
    harness_version: str,
) -> Path:
    path = (
        Path(repo_root)
        / "data"
        / "harness_task_score"
        / f"harness_v_{harness_version}.tsv"
    )
    _write_rows(path, TASK_SCORE_HEADER, [])
    return path


def clear_task_set_scores(
    repo_root: str | Path,
    harness_version: str,
) -> Path:
    path = (
        Path(repo_root)
        / "data"
        / "harness_task_set_score"
        / f"harness_v_{harness_version}.tsv"
    )
    _write_rows(path, TASK_SET_SCORE_HEADER, [])
    return path


def has_harness_info(
    repo_root: str | Path,
    harness_version: str,
) -> bool:
    path = Path(repo_root) / "data" / "harness_info" / "harness_info.tsv"
    rows = _read_rows(path, HARNESS_INFO_HEADER, keep_spaces_in_last=True)
    return any(
        row.get("harness_version") == str(harness_version)
        for row in rows
    )


def ensure_harness_info(
    repo_root: str | Path,
    *,
    harness_version: str,
    parent_version: str | None = None,
    description: str = "",
) -> Path:
    """Add a row for ``harness_version`` if it is not present yet.

    An existing row is never overwritten: descriptions are edited by hand.
    """
    repo_root = Path(repo_root)
    path = repo_root / "data" / "harness_info" / "harness_info.tsv"
    rows = _read_rows(path, HARNESS_INFO_HEADER, keep_spaces_in_last=True)

    if any(row["harness_version"] == harness_version for row in rows):
        # Normalize an existing space-separated file to TSV, keep the text.
        _write_rows(path, HARNESS_INFO_HEADER, rows)
        return path

    if parent_version is None:
        existing = sorted(
            row["harness_version"]
            for row in rows
            if row.get("harness_version")
        )
        parent_version = existing[-1] if existing else "0000"

    rows.append(
        {
            "harness_version": harness_version,
            "parent_harness_version": parent_version,
            "description": description or "auto-recorded by evaluation",
        }
    )
    rows.sort(key=lambda row: row["harness_version"])
    _write_rows(path, HARNESS_INFO_HEADER, rows)
    return path


def _read_rows(
    path: Path,
    header: tuple[str, ...],
    *,
    keep_spaces_in_last: bool = False,
) -> list[dict[str, str]]:
    """Read a TSV, mapping old column orders by column name.

    This lets an old file (for example ``task_id,harness_version,...``) be
    rewritten in the new column order without losing data.
    """
    if not path.is_file():
        return []
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not lines:
        return []

    file_header = _split_header(lines[0])
    rows: list[dict[str, str]] = []
    for line in lines[1:]:
        parts = _split_row(line, len(file_header), keep_spaces_in_last)
        by_name = dict(zip(file_header, parts))
        rows.append({column: by_name.get(column, "") for column in header})
    return rows


def _split_header(line: str) -> list[str]:
    if "\t" in line:
        return [part.strip() for part in line.split("\t")]
    return line.split()


def _split_row(line: str, fields: int, keep_spaces_in_last: bool) -> list[str]:
    if "\t" in line:
        parts = line.split("\t")
    elif keep_spaces_in_last:
        parts = line.split(None, fields - 1)
    else:
        parts = line.split()
    parts = [part.strip() for part in parts]
    if len(parts) < fields:
        parts += [""] * (fields - len(parts))
    return parts[:fields]


def _write_rows(path: Path, header: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["\t".join(header)]
    for row in rows:
        values = [
            _clean_cell(str(row.get(column, "")))
            for column in header
        ]
        lines.append("\t".join(values))
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _clean_cell(value: str) -> str:
    return value.replace("\t", " ").replace("\r", " ").replace("\n", " ").strip()


def _upsert(
    rows: list[dict[str, str]],
    key_fields: tuple[str, ...],
    new_row: dict[str, str],
) -> None:
    for index, row in enumerate(rows):
        if all(row.get(field) == new_row.get(field) for field in key_fields):
            rows[index] = new_row
            return
    rows.append(new_row)


def _format_bool(value: bool) -> str:
    return "true" if bool(value) else "false"


def _format_seconds(seconds: float) -> str:
    return f"{max(0.0, float(seconds)):.3f}"


def _format_score(score: float) -> str:
    return f"{float(score):g}"
