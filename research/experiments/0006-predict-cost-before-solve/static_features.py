#!/usr/bin/env python3
"""Static, pre-solve features of a task.

Only signals available before the first model call are used:

* the instruction text from ``task.json``;
* the files under ``workspace/``;
* the task category and reward.

Deliberately excluded from the honest feature set: ``solvable``, ``check``,
``expected`` and the numeric task id.  Those fields are part of the synthetic
generator's bookkeeping and would leak the label.  ``--with-meta-leak`` adds
them so the leak can be measured separately.

Usage::

    python research/experiments/0006-predict-cost-before-solve/static_features.py \
        --tasks-dir data/task \
        --out research/experiments/0006-predict-cost-before-solve/results/static_features.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]

TEXT_READ_LIMIT = 200_000
MAX_LINES = 200_000
CSV_SAMPLE_ROWS = 5_000
MAX_FILES_SCANNED = 2_000

SKIP_NAMES = {"answer.txt", "verdict.txt", ".DS_Store", ".gitkeep"}
SKIP_PREFIXES = (".harness_step_", "__pycache__")

TEXT_EXTS = {".txt", ".md", ".py", ".csv", ".tsv", ".json", ".jsonl", ".log",
             ".yaml", ".yml", ".html", ".sql", ".sh", ".ini", ".cfg", ".toml",
             ".xml", ".rst"}
CODE_EXTS = {".py", ".js", ".ts", ".sh", ".go", ".rs", ".java", ".c", ".cpp"}
DATA_EXTS = {".csv", ".tsv", ".json", ".jsonl", ".parquet", ".sqlite", ".db"}

FILE_NAME_RE = re.compile(
    r"\b[\w./-]+\.(?:csv|tsv|json|jsonl|txt|md|py|log|yaml|yml|html|sql|sh|"
    r"zip|gz|parquet|ini|cfg|toml)\b",
    re.IGNORECASE,
)
BACKTICK_RE = re.compile(r"`([^`]+)`")
NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z_'-]*")

GROUPS = {
    "inspect": {"read", "inspect", "look", "find", "locate", "search", "grep",
                "open", "show", "list", "scan", "which", "where"},
    "compute": {"compute", "calculate", "count", "sum", "total", "average",
                "mean", "median", "max", "min", "maximum", "minimum", "how",
                "many", "much", "percentage", "ratio", "product", "multiply",
                "divide", "subtract"},
    "modify": {"fix", "implement", "edit", "modify", "write", "add", "remove",
               "refactor", "change", "update", "create", "rename", "replace",
               "make", "run", "use"},
    "verify": {"test", "tests", "verify", "check", "validate", "pass", "passes",
               "fail", "fails", "assert", "unittest", "pytest"},
    "data": {"sort", "group", "join", "merge", "filter", "aggregate", "parse",
             "convert", "extract", "select", "query", "clean", "deduplicate",
             "pivot", "split", "combine"},
    "logic": {"prove", "determine", "whether", "if", "else", "condition",
              "constraint", "guarantee", "exists", "possible", "impossible",
              "contradict", "consistent", "unique"},
    "math": {"integer", "prime", "divisible", "modulo", "equation", "polynomial",
             "probability", "combinatorics", "permutation", "sequence", "sum",
             "digits", "remainder", "gcd", "lcm", "rectangle", "triangle"},
    "step": {"then", "next", "after", "finally", "first", "second", "third",
             "step", "repeat", "until", "while", "for", "each"},
}

BOILERPLATE_MARKERS = (
    "Work only inside the current directory.",
    "When you are done, write ONLY",
)


def _strip_boilerplate(text: str) -> str:
    cut = len(text)
    for marker in BOILERPLATE_MARKERS:
        pos = text.find(marker)
        if pos >= 0:
            cut = min(cut, pos)
    return text[:cut].strip()


def instruction_features(text: str) -> dict[str, Any]:
    core = _strip_boilerplate(text)
    words = WORD_RE.findall(core.lower())
    word_set = set(words)
    backticks = BACKTICK_RE.findall(core)
    numbers = NUMBER_RE.findall(core)
    sentences = [s for s in re.split(r"[.!?]+", core) if s.strip()]
    clauses = [c for c in re.split(r"[;,](?:\s|$)|\band then\b|\bthen\b",
                                    core, flags=re.IGNORECASE) if c.strip()]
    feats: dict[str, Any] = {
        "ins_chars": len(core),
        "ins_words": len(words),
        "ins_unique_words": len(word_set),
        "ins_sentences": len(sentences),
        "ins_clauses": len(clauses),
        "ins_lines": core.count("\n") + 1,
        "ins_digits": sum(ch.isdigit() for ch in core),
        "ins_numbers": len(numbers),
        "ins_max_number_digits": max((len(n.lstrip("-").replace(".", ""))
                                      for n in numbers), default=0),
        "ins_backticks": len(backticks),
        "ins_unique_backticks": len(set(backticks)),
        "ins_file_names": len(set(FILE_NAME_RE.findall(core))),
        "ins_question_marks": core.count("?"),
        "ins_commas": core.count(","),
        "ins_semicolons": core.count(";"),
        "ins_parentheses": core.count("(") + core.count(")"),
        "ins_uppercase_ratio": (
            sum(ch.isupper() for ch in core) / max(1, sum(ch.isalpha() for ch in core))
        ),
        "ins_avg_word_len": len(core) / max(1, len(words)),
    }
    for name, group in GROUPS.items():
        counts = sum(1 for w in words if w in group)
        feats[f"ins_kw_{name}"] = counts
        feats[f"ins_kw_{name}_per100"] = 100.0 * counts / max(1, len(words))
    # The original instruction (with the submission boilerplate) is what the
    # model sees; keep its length as a separate feature.
    feats["ins_chars_raw"] = len(text)
    feats["ins_words_raw"] = len(WORD_RE.findall(text.lower()))
    return feats


def _read_text(path: Path, limit: int = TEXT_READ_LIMIT) -> str | None:
    try:
        raw = path.read_bytes()[:limit]
    except OSError:
        return None
    if b"\x00" in raw:
        return None
    try:
        return raw.decode("utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return None


def _count_lines(path: Path, limit: int = MAX_LINES) -> tuple[int, bool]:
    n = 0
    try:
        with path.open("rb") as fh:
            for _ in fh:
                n += 1
                if n >= limit:
                    return n, True
    except OSError:
        return 0, False
    return n, False


def _csv_shape(path: Path) -> tuple[int, int]:
    rows = 0
    cols = 0
    try:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as fh:
            reader = csv.reader(fh)
            for i, row in enumerate(reader):
                if i == 0:
                    cols = len(row)
                rows += 1
                if rows >= CSV_SAMPLE_ROWS:
                    break
    except OSError:
        pass
    return rows, cols


def _json_depth(value: Any, depth: int = 0) -> int:
    if isinstance(value, dict) and value:
        return 1 + max(_json_depth(v, depth + 1) for v in value.values())
    if isinstance(value, list) and value:
        return 1 + max(_json_depth(v, depth + 1) for v in value)
    return depth


def workspace_features(workspace: Path) -> dict[str, Any]:
    feats: dict[str, Any] = {
        "ws_files": 0,
        "ws_dirs": 0,
        "ws_bytes": 0,
        "ws_text_bytes": 0,
        "ws_binary_files": 0,
        "ws_empty_files": 0,
        "ws_total_lines": 0,
        "ws_max_file_bytes": 0,
        "ws_max_file_lines": 0,
        "ws_mean_file_bytes": 0.0,
        "ws_max_depth": 0,
        "ws_top_entries": 0,
        "ws_py_files": 0,
        "ws_py_lines": 0,
        "ws_test_files": 0,
        "ws_test_bytes": 0,
        "ws_csv_files": 0,
        "ws_csv_rows": 0,
        "ws_csv_max_rows": 0,
        "ws_csv_max_cols": 0,
        "ws_json_files": 0,
        "ws_jsonl_files": 0,
        "ws_jsonl_lines": 0,
        "ws_md_files": 0,
        "ws_txt_files": 0,
        "ws_log_files": 0,
        "ws_data_files": 0,
        "ws_code_files": 0,
        "ws_has_tests": 0,
        "ws_text_words": 0,
        "ws_py_defs": 0,
        "ws_py_classes": 0,
        "ws_py_asserts": 0,
    }
    if not workspace.exists():
        return feats
    files = []
    for path in workspace.rglob("*"):
        if len(files) >= MAX_FILES_SCANNED:
            break
        if path.is_dir():
            feats["ws_dirs"] += 1
            continue
        if not path.is_file():
            continue
        name = path.name
        if name in SKIP_NAMES or any(part.startswith(SKIP_PREFIXES) or
                                     part == "__pycache__"
                                     for part in path.parts):
            continue
        files.append(path)

    total_lines = 0
    max_lines = 0
    for path in files:
        try:
            size = path.stat().st_size
        except OSError:
            continue
        ext = path.suffix.lower()
        depth = len(path.relative_to(workspace).parts) - 1
        feats["ws_files"] += 1
        feats["ws_bytes"] += size
        feats["ws_max_file_bytes"] = max(feats["ws_max_file_bytes"], size)
        feats["ws_max_depth"] = max(feats["ws_max_depth"], depth)
        if size == 0:
            feats["ws_empty_files"] += 1
        if ext in TEXT_EXTS:
            feats["ws_text_bytes"] += size
            text = _read_text(path)
            if text is not None:
                feats["ws_text_words"] += len(WORD_RE.findall(text))
                lines, truncated = _count_lines(path)
                total_lines += lines
                max_lines = max(max_lines, lines)
        else:
            feats["ws_binary_files"] += 1

        if ext in CODE_EXTS:
            feats["ws_code_files"] += 1
        if ext in DATA_EXTS:
            feats["ws_data_files"] += 1
        if ext == ".py":
            feats["ws_py_files"] += 1
            text = _read_text(path) or ""
            lines = text.count("\n") + (1 if text else 0)
            feats["ws_py_lines"] += lines
            feats["ws_py_defs"] += len(re.findall(r"^\s*def\s+\w+", text, re.M))
            feats["ws_py_classes"] += len(re.findall(r"^\s*class\s+\w+", text, re.M))
            feats["ws_py_asserts"] += len(re.findall(r"\bassert\b", text))
        is_test = (
            path.name.startswith("test_")
            or path.name.endswith("_test.py")
            or "test" in path.name.lower() and ext == ".py"
        )
        if is_test:
            feats["ws_test_files"] += 1
            feats["ws_test_bytes"] += size
        if ext == ".csv":
            feats["ws_csv_files"] += 1
            rows, cols = _csv_shape(path)
            feats["ws_csv_rows"] += rows
            feats["ws_csv_max_rows"] = max(feats["ws_csv_max_rows"], rows)
            feats["ws_csv_max_cols"] = max(feats["ws_csv_max_cols"], cols)
        elif ext == ".json":
            feats["ws_json_files"] += 1
        elif ext == ".jsonl":
            feats["ws_jsonl_files"] += 1
            lines, _ = _count_lines(path)
            feats["ws_jsonl_lines"] += lines
        elif ext == ".md":
            feats["ws_md_files"] += 1
        elif ext == ".txt":
            feats["ws_txt_files"] += 1
        elif ext == ".log":
            feats["ws_log_files"] += 1

    feats["ws_total_lines"] = total_lines
    feats["ws_max_file_lines"] = max_lines
    if feats["ws_files"]:
        feats["ws_mean_file_bytes"] = feats["ws_bytes"] / feats["ws_files"]
    feats["ws_has_tests"] = int(feats["ws_test_files"] > 0)
    try:
        feats["ws_top_entries"] = len(list(workspace.iterdir()))
    except OSError:
        feats["ws_top_entries"] = 0
    return feats


def overview_features(text: str) -> dict[str, float]:
    """The same overview signals that experiment 0007 extracts from a turn."""
    return {
        "overview_chars": float(len(text)),
        "overview_lines": float(text.count("\n") + (1 if text else 0)),
        "overview_fails": float(len(re.findall(
            r"\b(?:FAIL|FAILED|ERROR|Traceback)\b", text))),
        "overview_passes": float(len(re.findall(
            r"\b(?:PASS|PASSED|OK|passed)\b", text))),
        "overview_notimplemented": float(text.count("NotImplementedError")),
        "overview_asserts": float(text.count("AssertionError")),
        "overview_syntax": float(text.count("SyntaxError")),
        "overview_typeerror": float(text.count("TypeError")),
        "overview_filenames": float(len(set(re.findall(
            r"\b[\w.-]+\.(?:csv|tsv|json|jsonl|txt|md|py|log|yaml|yml)\b",
            text)))),
        "overview_dollar_lines": float(text.count("$ ")),
        "tests_in_overview": float("$ tests" in text),
    }


def load_tasks(
    tasks_dir: Path, with_overview: bool = False
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    # Training data is category/label/number/task.json; the organizer set and
    # the hidden set are flat: <task_id>/task.json.  Support both.
    paths = sorted(tasks_dir.glob("*/[!.]*/[!.]*/task.json"))
    if not paths:
        paths = sorted(tasks_dir.glob("*/task.json"))
    for tj in paths:
        try:
            meta = json.loads(tj.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rel_parts = tj.parent.relative_to(tasks_dir).parts
        if len(rel_parts) >= 3:
            label = rel_parts[-2]
        else:
            label = "unknown"
        rel = "/".join(rel_parts) if rel_parts else tj.parent.name
        row: dict[str, Any] = {
            "rel": rel,
            "task_id": meta.get("task_id", rel),
            "task_type": meta.get("task_type", rel_parts[0] if rel_parts else "unknown"),
            "label": label,
            "reward": float(meta.get("reward", 0.0)),
            "instruction": meta.get("instruction", ""),
            "check": meta.get("check", ""),
            "has_expected": int("expected" in meta),
            "has_solvable_field": int("solvable" in meta),
        }
        row.update(instruction_features(row["instruction"]))
        row.update(workspace_features(tj.parent / "workspace"))
        if with_overview:
            try:
                from harness.application.overview import (  # noqa: PLC0415
                    OverviewLimits, build_overview,
                )
                workspace = tj.parent / "workspace"
                overview = build_overview(
                    workspace if workspace.is_dir() else tj.parent,
                    row["instruction"],
                    OverviewLimits(max_tokens=1500, max_test_output_chars=2200),
                )
                row.update(overview_features(overview))
            except Exception:  # noqa: BLE001 - overview is optional
                row.update({key: float("nan") for key in (
                    "overview_chars", "overview_lines", "overview_fails",
                    "overview_passes", "overview_notimplemented",
                    "overview_asserts", "overview_syntax", "overview_typeerror",
                    "overview_filenames", "overview_dollar_lines",
                    "tests_in_overview",
                )})
        rows.append(row)
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-dir", type=Path, default=ROOT / "data" / "task")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--with-meta-leak", action="store_true",
                        help="add check/expected/solvable fields (leak model)")
    parser.add_argument("--with-overview", action="store_true",
                        help="run the harness overview builder (tests included)")
    args = parser.parse_args(argv)

    rows = load_tasks(args.tasks_dir, with_overview=args.with_overview)
    if not args.with_meta_leak:
        for row in rows:
            row.pop("check", None)
            row.pop("has_expected", None)
            row.pop("has_solvable_field", None)
    for row in rows:
        row.pop("instruction", None)
        label = row["label"]
        if label == "solvable":
            row["label"] = 1
            row["is_impossible_dir"] = 0
        elif label == "impossible":
            row["label"] = 0
            row["is_impossible_dir"] = 1
        else:
            row["label"] = -1
            row["is_impossible_dir"] = -1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows x {len(fieldnames)} columns to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
