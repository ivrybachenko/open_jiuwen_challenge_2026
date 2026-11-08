"""Measure the repository size and compare it with the competition limit.

The competition allows a repository smaller than 100 MB without ``.git``. The
number the jury effectively sees is the size of the files tracked by git, so
that is the default metric. The working tree (which may contain a local
``.venv``) and the total size including ``.git`` are reported next to it.
"""

from __future__ import annotations

import heapq
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from evaluation.common.reporting import format_size

DEFAULT_MAX_REPO_BYTES = 100_000_000  # 100 MB, competition limit

METRICS = ("tracked", "without-git", "total")

GIT_DIR = ".git"

# Directories that usually exist locally but are not committed. They are not
# excluded from the measurements, only highlighted in the report.
LOCAL_ONLY_DIRS = frozenset(
    {
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".git",
        "out",
    }
)


@dataclass
class TopLevelEntry:
    """Usage of one entry directly under the repository root."""

    name: str
    bytes: int = 0
    files: int = 0
    tracked_bytes: int = 0

    @property
    def untracked_bytes(self) -> int:
        return max(0, self.bytes - self.tracked_bytes)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "bytes": self.bytes,
            "human": format_size(self.bytes),
            "files": self.files,
            "tracked_bytes": self.tracked_bytes,
            "untracked_bytes": self.untracked_bytes,
        }


@dataclass
class FileEntry:
    path: str
    bytes: int

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "bytes": self.bytes,
            "human": format_size(self.bytes),
        }


@dataclass
class RepoSizeReport:
    repo: Path
    max_bytes: int
    metric: str = "tracked"
    total_bytes: int = 0
    git_bytes: int = 0
    without_git_bytes: int = 0
    tracked_bytes: int | None = None
    tracked_files: int = 0
    top_level: list[TopLevelEntry] = field(default_factory=list)
    largest_files: list[FileEntry] = field(default_factory=list)

    @property
    def measured_bytes(self) -> int:
        """Size checked against the limit for the selected metric."""
        if self.metric == "total":
            return self.total_bytes
        if self.metric == "without-git":
            return self.without_git_bytes
        if self.tracked_bytes is not None:
            return self.tracked_bytes
        # No git metadata available: fall back to the working tree size.
        return self.without_git_bytes

    @property
    def measured_source(self) -> str:
        if self.metric == "total":
            return "every file, including .git"
        if self.metric == "without-git":
            return "working tree without .git"
        if self.tracked_bytes is not None:
            return "files tracked by git"
        return "working tree without .git (git metadata unavailable)"

    @property
    def untracked_bytes(self) -> int | None:
        if self.tracked_bytes is None:
            return None
        return max(0, self.without_git_bytes - self.tracked_bytes)

    @property
    def ok(self) -> bool:
        return self.measured_bytes <= self.max_bytes

    def to_dict(self) -> dict:
        return {
            "repo": str(self.repo),
            "metric": self.metric,
            "measured_source": self.measured_source,
            "measured_bytes": self.measured_bytes,
            "measured_human": format_size(self.measured_bytes),
            "limit_bytes": self.max_bytes,
            "limit_human": format_size(self.max_bytes),
            "ok": self.ok,
            "sizes": {
                "total_bytes": self.total_bytes,
                "total_human": format_size(self.total_bytes),
                "git_bytes": self.git_bytes,
                "git_human": format_size(self.git_bytes),
                "without_git_bytes": self.without_git_bytes,
                "without_git_human": format_size(self.without_git_bytes),
                "tracked_bytes": self.tracked_bytes,
                "tracked_human": (
                    format_size(self.tracked_bytes)
                    if self.tracked_bytes is not None
                    else None
                ),
                "tracked_files": self.tracked_files,
                "untracked_bytes": self.untracked_bytes,
                "untracked_human": (
                    format_size(self.untracked_bytes)
                    if self.untracked_bytes is not None
                    else None
                ),
            },
            "top_level": [entry.to_dict() for entry in self.top_level],
            "largest_files": [entry.to_dict() for entry in self.largest_files],
        }


def scan_tree(
    root: str | Path,
    *,
    largest_n: int = 10,
    largest_min_bytes: int = 0,
) -> tuple[int, dict[str, tuple[int, int]], list[FileEntry]]:
    """Walk ``root`` once and return total size, per-root-entry usage and largest files.

    The tree is walked without following symlinks, so the result always
    terminates even for circular links. Entries that cannot be read are
    silently skipped, like ``du`` does.
    """
    root = Path(root)

    total = 0
    per_entry: dict[str, list[int]] = {}
    largest: list[tuple[int, str]] = []

    stack: list[tuple[Path, str | None]] = [(root, None)]
    while stack:
        directory, group = stack.pop()
        try:
            with os.scandir(directory) as iterator:
                entries = list(iterator)
        except OSError:
            continue
        for entry in entries:
            name = entry.name
            try:
                is_dir = entry.is_dir(follow_symlinks=False)
                size = 0 if is_dir else entry.stat(follow_symlinks=False).st_size
            except OSError:
                continue

            if group is None:
                current_group = name
                per_entry.setdefault(current_group, [0, 0])
            else:
                current_group = group

            if is_dir:
                stack.append((Path(entry.path), current_group))
                continue

            total += size
            per_entry[current_group][0] += size
            per_entry[current_group][1] += 1
            if largest_n > 0 and size >= largest_min_bytes:
                relative = str(Path(entry.path).relative_to(root))
                if len(largest) < largest_n:
                    heapq.heappush(largest, (size, relative))
                elif size > largest[0][0]:
                    heapq.heapreplace(largest, (size, relative))

    usage = {name: (values[0], values[1]) for name, values in per_entry.items()}
    top_files = [
        FileEntry(path=path, bytes=size)
        for size, path in sorted(largest, reverse=True)
    ]
    return total, usage, top_files


def git_tracked_sizes(repo: str | Path) -> tuple[dict[str, int], int] | None:
    """Return per-root-entry tracked sizes and the tracked file count.

    ``None`` means the directory is not a git repository or git is missing;
    callers then fall back to the plain working-tree size.
    """
    repo = Path(repo)
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "-z"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=120.0,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None

    per_entry: dict[str, int] = {}
    count = 0
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        relative = raw.decode("utf-8", errors="surrogateescape")
        path = repo / relative
        try:
            size = path.stat().st_size
        except OSError:
            continue
        count += 1
        component = PurePosixPath(relative).parts[0]
        per_entry[component] = per_entry.get(component, 0) + size
    return per_entry, count


def check_repo_size(
    *,
    repo: str | Path,
    max_bytes: int = DEFAULT_MAX_REPO_BYTES,
    metric: str = "tracked",
    top_n: int = 20,
    largest_n: int = 10,
) -> RepoSizeReport:
    """Measure ``repo`` and build a report for the selected metric."""
    if metric not in METRICS:
        raise ValueError(f"unknown metric: {metric!r}; expected one of {METRICS}")

    repo = Path(repo).expanduser().resolve()
    if not repo.is_dir():
        raise NotADirectoryError(f"repository directory not found: {repo}")

    total, usage, largest = scan_tree(
        repo,
        largest_n=largest_n,
        largest_min_bytes=1,
    )
    git_bytes, _ = usage.get(GIT_DIR, (0, 0))
    without_git = max(0, total - git_bytes)

    tracked_sizes = git_tracked_sizes(repo)
    report = RepoSizeReport(
        repo=repo,
        max_bytes=max_bytes,
        metric=metric,
        total_bytes=total,
        git_bytes=git_bytes,
        without_git_bytes=without_git,
        largest_files=largest,
    )

    tracked_map: dict[str, int] = {}
    if tracked_sizes is not None:
        tracked_map, report.tracked_files = tracked_sizes
        report.tracked_bytes = sum(tracked_map.values())

    entries = [
        TopLevelEntry(
            name=name,
            bytes=size,
            files=count,
            tracked_bytes=tracked_map.get(name, 0),
        )
        for name, (size, count) in usage.items()
        if name != GIT_DIR
    ]
    report.top_level = sorted(entries, key=lambda item: item.bytes, reverse=True)
    if top_n > 0:
        report.top_level = report.top_level[:top_n]
    return report
