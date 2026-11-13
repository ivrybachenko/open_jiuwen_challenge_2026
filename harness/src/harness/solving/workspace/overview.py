"""Build a compact, bounded overview of a task workspace.

The overview is the only context the agent gets before its first bash script.
It must be useful on ordinary tasks and harmless on hostile ones: a directory
with 20k files, a multi-gigabyte file, a first line longer than the budget, or
a test suite that hangs.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from harness.solving.workspace.shell import run_process

IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    ".idea",
    ".vscode",
    "dist",
    "build",
    ".eggs",
    ".ipynb_checkpoints",
}
DATASET_SUFFIXES = {".csv", ".tsv", ".psv"}
IGNORED_FILES = {".DS_Store", "Thumbs.db"}


@dataclass(frozen=True)
class OverviewLimits:
    max_tokens: int = 1500
    max_entries_scanned: int = 3000
    max_entries_shown: int = 80
    max_depth: int = 4
    per_dir_cap: int = 800
    max_dataset_files: int = 80
    max_dataset_groups: int = 12
    max_dataset_examples: int = 4
    max_header_chars: int = 240
    max_task_chars: int = 2500
    max_test_files: int = 6
    test_timeout: float = 20.0
    test_total_timeout: float = 60.0
    max_test_output_chars: int = 2200

    @property
    def max_chars(self) -> int:
        return max(1500, int(self.max_tokens) * 4)


@dataclass(frozen=True)
class FsEntry:
    rel: str
    is_dir: bool
    size: int
    depth: int


@dataclass
class ScanResult:
    entries: list[FsEntry] = field(default_factory=list)
    truncated: bool = False
    scanned: int = 0


def build_overview(
    workspace: Path,
    instruction: str,
    limits: OverviewLimits | None = None,
) -> str:
    """Return a terminal-style overview that fits ``limits.max_tokens``."""
    limits = limits or OverviewLimits()
    workspace = Path(workspace).resolve()

    scan = scan_workspace(workspace, limits)
    pieces: dict[str, str] = {}
    pieces["pwd"] = _pwd_section(workspace, scan)
    pieces["listing"] = format_listing(scan.entries, scan, limits)
    pieces["datasets"] = describe_datasets(workspace, scan, limits)
    pieces["tests"] = run_task_tests(workspace, limits)
    pieces["task"] = _task_section(instruction, limits.max_task_chars)

    return _fit_sections(pieces, limits.max_chars)


def _pwd_section(workspace: Path, scan: ScanResult) -> str:
    python = sys.executable or "python3"
    return f"$ pwd\n{workspace}\n$ which python\n{python}"


def scan_workspace(workspace: Path, limits: OverviewLimits) -> ScanResult:
    """Breadth-first scan with hard caps; never follows symlinks."""
    result = ScanResult()
    if not workspace.is_dir():
        result.truncated = True
        return result

    queue: list[tuple[Path, str, int]] = [(workspace, "", 0)]
    while queue and result.scanned < limits.max_entries_scanned:
        abs_dir, rel_dir, depth = queue.pop(0)
        if depth >= limits.max_depth:
            continue
        try:
            with os.scandir(abs_dir) as iterator:
                raw = []
                for item in iterator:
                    raw.append(item)
                    if len(raw) >= limits.per_dir_cap:
                        result.truncated = True
                        break
        except OSError:
            result.truncated = True
            continue

        raw.sort(key=lambda item: item.name.lower())
        for item in raw:
            if result.scanned >= limits.max_entries_scanned:
                result.truncated = True
                break
            if (
                item.name in {".", ".."}
                or item.name in IGNORED_FILES
                or item.name.startswith(".harness_")
            ):
                continue
            rel = f"{rel_dir}/{item.name}" if rel_dir else item.name
            try:
                is_dir = item.is_dir(follow_symlinks=False)
                is_symlink = item.is_symlink()
                size = 0 if is_dir or is_symlink else item.stat(
                    follow_symlinks=False
                ).st_size
            except OSError:
                is_dir = False
                size = -1
            result.entries.append(
                FsEntry(rel=rel, is_dir=is_dir, size=size, depth=depth + 1)
            )
            result.scanned += 1
            if is_dir and not item.is_symlink():
                queue.append((Path(item.path), rel, depth + 1))
    if queue:
        result.truncated = True
    return result


def format_listing(
    entries: list[FsEntry],
    scan: ScanResult,
    limits: OverviewLimits,
) -> str:
    if not entries:
        text = "$ ls\n(empty)"
        if scan.truncated:
            text += "\n(scan stopped early)"
        return text

    files = [entry for entry in entries if not entry.is_dir]
    groups: dict[tuple[str, str], list[FsEntry]] = {}
    for entry in files:
        groups.setdefault(_file_group_key(entry.rel), []).append(entry)
    large_groups = {
        key for key, members in groups.items() if len(members) > 8
    }

    items: list[str] = []
    seen_groups: set[tuple[str, str]] = set()
    for entry in entries:
        if entry.is_dir:
            items.append(f"{entry.rel}/")
            continue
        key = _file_group_key(entry.rel)
        if key in large_groups:
            if key in seen_groups:
                continue
            seen_groups.add(key)
            members = groups[key]
            for sample in members[:3]:
                items.append(_format_file(sample))
            parent, suffix = key
            pattern = f"{parent}/*{suffix}" if parent else f"*{suffix}"
            total = sum(max(0, sample.size) for sample in members)
            count = f"{len(members)}" + ("+" if scan.truncated else "")
            size_text = f", {_human_size(total)}" if total else ""
            more = len(members) - min(3, len(members))
            more_text = f", {more} more" if more > 0 else ""
            items.append(f"{pattern}  ({count} files{size_text}{more_text})")
        else:
            items.append(_format_file(entry))

    shown = items[: limits.max_entries_shown]
    if len(items) > limits.max_entries_shown:
        shown.append(f"... {len(items) - limits.max_entries_shown} more entries")
    if scan.truncated:
        shown.append("... (scan stopped early)")
    return "\n".join(["$ ls", *shown])


def _file_group_key(rel: str) -> tuple[str, str]:
    parent, name = os.path.split(rel)
    _, suffix = os.path.splitext(name)
    return parent, suffix.lower()


def _format_file(entry: FsEntry) -> str:
    if entry.size >= 1_000_000:
        return f"{entry.rel}  ({_human_size(entry.size)})"
    if entry.size < 0:
        return f"{entry.rel}  (unreadable)"
    return entry.rel


def describe_datasets(
    workspace: Path,
    scan: ScanResult,
    limits: OverviewLimits,
) -> str:
    candidates = [
        entry
        for entry in scan.entries
        if not entry.is_dir and os.path.splitext(entry.rel)[1].lower() in DATASET_SUFFIXES
    ]
    if not candidates:
        return ""
    candidates.sort(key=lambda entry: entry.rel)
    sampled = len(candidates) > limits.max_dataset_files
    candidates = candidates[: limits.max_dataset_files]

    groups: dict[str, list[dict[str, str]]] = {}
    for entry in candidates:
        parsed = _read_dataset_head(workspace, entry.rel, limits.max_header_chars)
        if parsed is None:
            continue
        header, row = parsed
        groups.setdefault(header, []).append({"file": entry.rel, "row": row})
    if not groups:
        return ""

    lines = ["$ datasets"]
    if len(groups) == 1:
        header, rows = next(iter(groups.items()))
        count = len(rows)
        count_text = f"{count}" + ("+" if sampled else "")
        lines.append(f"{count_text} files, same header: {header}")
        if rows[0]["row"]:
            lines.append(f"example row: {rows[0]['row']}")
        files = ", ".join(item["file"] for item in rows[: limits.max_dataset_examples])
        if count > limits.max_dataset_examples:
            files += f", ... (+{count - limits.max_dataset_examples})"
        lines.append(f"files: {files}")
    else:
        lines.append(
            f"{len(candidates)} files, {len(groups)} distinct headers"
            + (" (sampled)" if sampled else "")
        )
        for index, (header, rows) in enumerate(groups.items()):
            if index >= limits.max_dataset_groups:
                lines.append(f"... {len(groups) - limits.max_dataset_groups} more headers")
                break
            lines.append(f"header: {header}")
            if rows[0]["row"]:
                lines.append(f"  example row: {rows[0]['row']}")
            files = ", ".join(
                item["file"] for item in rows[: limits.max_dataset_examples]
            )
            if len(rows) > limits.max_dataset_examples:
                files += f", ... (+{len(rows) - limits.max_dataset_examples})"
            lines.append(f"  files: {files}")
    if scan.truncated:
        lines.append("(dataset list may be incomplete: scan stopped early)")
    return "\n".join(lines)


def _read_dataset_head(
    workspace: Path,
    rel: str,
    max_chars: int,
) -> tuple[str, str] | None:
    path = workspace / rel
    try:
        with path.open("rb") as stream:
            data = stream.read(4096)
    except OSError:
        return None
    if b"\x00" in data:
        return None
    text = data.decode("utf-8", errors="replace")
    lines = text.splitlines()
    if not lines:
        return None
    header = _clean_cell(lines[0], max_chars)
    if not header:
        return None
    row = ""
    if len(lines) > 1:
        row = _clean_cell(lines[1], max_chars)
    return header, row


def _clean_cell(value: str, max_chars: int) -> str:
    value = value.replace("\t", " | ").strip()
    if len(value) > max_chars:
        value = value[:max_chars] + "...[truncated]"
    return value


def run_task_tests(workspace: Path, limits: OverviewLimits) -> str:
    test_files = find_test_files(workspace, limits)
    if not test_files:
        return ""

    lines = ["$ tests"]
    passed = 0
    failed = 0
    budget_left = limits.test_total_timeout
    for test_file in test_files[: limits.max_test_files]:
        if budget_left <= 0:
            lines.append("... (test time limit reached)")
            break
        result = run_process(
            [sys.executable or "python3", str(test_file)],
            cwd=workspace,
            timeout=min(limits.test_timeout, budget_left),
            max_output_chars=limits.max_test_output_chars,
        )
        budget_left -= result.duration_seconds
        try:
            rel = str(test_file.relative_to(workspace))
        except ValueError:
            rel = str(test_file)
        if result.ok:
            passed += 1
            if result.output.strip():
                lines.append(f"{rel}: PASS")
                lines.append(_clip(result.output.strip(), 800))
            else:
                lines.append(f"{rel}: PASS (no output)")
        elif result.timed_out:
            failed += 1
            lines.append(f"{rel}: TIMEOUT after {result.duration_seconds:.0f}s")
        elif result.error:
            failed += 1
            lines.append(f"{rel}: ERROR {result.error}")
        else:
            failed += 1
            lines.append(f"{rel}: FAIL (exit {result.exit_code})")
            lines.append(_clip(result.output.strip(), limits.max_test_output_chars))
    skipped = max(0, len(test_files) - limits.max_test_files)
    if skipped:
        lines.append(f"... {skipped} more test files not run")
    if failed == 0 and passed:
        lines.append(f"result: all {passed} tests pass")
    elif failed:
        lines.append(f"result: {failed} failing, {passed} passing")
    return "\n".join(line for line in lines if line != "")


def find_test_files(workspace: Path, limits: OverviewLimits) -> list[Path]:
    found: list[Path] = []
    visited_dirs = 0
    for root, dirs, files in os.walk(workspace):
        visited_dirs += 1
        if visited_dirs > 500 or len(found) >= limits.max_test_files * 3:
            break
        dirs[:] = sorted(
            name for name in dirs if name not in IGNORED_DIRS
        )
        for name in sorted(files):
            if name.startswith("test") and name.endswith(".py"):
                found.append(Path(root) / name)
                if len(found) >= limits.max_test_files * 3:
                    break
    return found


def _task_section(instruction: str, max_chars: int) -> str:
    text = (instruction or "").strip()
    if len(text) > max_chars:
        text = text[:max_chars] + "\n...[task text truncated]"
    return (
        f"$ cat task.txt\n{text}\n"
        "$ # Reply with one complete script that solves the task and writes answer.txt."
    )


def _fit_sections(pieces: dict[str, str], max_chars: int) -> str:
    order = ["pwd", "listing", "datasets", "tests", "task"]
    caps = {
        "pwd": 400,
        "listing": min(3000, int(max_chars * 0.26)),
        "datasets": min(2500, int(max_chars * 0.15)),
        "tests": min(2500, int(max_chars * 0.20)),
        "task": min(2500, int(max_chars * 0.31)),
    }
    clipped = {
        name: _clip(pieces.get(name, ""), caps.get(name, 1000), both=name == "tests")
        for name in order
    }
    text = "\n".join(clipped[name] for name in order if clipped[name])
    if len(text) <= max_chars:
        return text

    # Keep the task text and shrink the optional sections first.
    for name in ("listing", "datasets", "tests"):
        if len(text) <= max_chars:
            break
        clipped[name] = _clip(clipped[name], 120)
        text = "\n".join(clipped[n] for n in order if clipped[n])
    if len(text) > max_chars:
        fixed = sum(
            len(clipped[name]) + 1 for name in ("pwd", "listing", "datasets", "tests")
        )
        room = max(200, max_chars - fixed)
        clipped["task"] = _clip(clipped["task"], room)
        text = "\n".join(clipped[n] for n in order if clipped[n])
    if len(text) > max_chars:
        text = _clip(text, max_chars)
    return text


def _clip(text: str, limit: int, *, tail: bool = False, both: bool = False) -> str:
    if limit <= 0:
        return ""
    if len(text) <= limit:
        return text
    note = "...[truncated]..."
    if limit <= len(note) + 10:
        return text[:limit]
    if both:
        head = max(1, (limit - len(note)) // 2)
        tail_len = max(1, limit - len(note) - head)
        return text[:head] + "\n" + note + "\n" + text[-tail_len:]
    if tail:
        return note + text[-(limit - len(note)) :]
    return text[: limit - len(note)] + note


def _human_size(size: int) -> str:
    value = float(max(0, size))
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(value)} B"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"
