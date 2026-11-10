"""Task model, task-set loading and test-file snapshots.

Task format (same as ``challenge_info/task-examples``)::

    <task-dir>/task.json
    <task-dir>/workspace/...        # optional; cwd for the agent

``task.json`` fields used here: ``task_id``, ``task_type``, ``instruction``,
``reward``, ``expected`` and ``check``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from evaluation.common.paths import default_tasks_root, repo_root


@dataclass(frozen=True)
class EvaluationTask:
    task_id: str
    task_type: str
    instruction: str
    reward: float
    expected: str | None
    check: str | None
    root: Path
    # Some challenge tasks are intentionally unsolvable; ``task.json`` may mark
    # them with ``"solvable": false`` or ``"impossible": true``.
    solvable: bool = True

    @property
    def workspace(self) -> Path:
        """Directory the agent works in (``workspace/`` or the task root)."""
        workspace = self.root / "workspace"
        return workspace if workspace.is_dir() else self.root

    @property
    def answer_paths(self) -> tuple[Path, ...]:
        """Where ``answer.txt`` may be written.

        The harness writes both the workspace copy and the task-root copy, so
        the evaluator accepts either.
        """
        paths = [self.workspace / "answer.txt"]
        if self.root != self.workspace:
            paths.append(self.root / "answer.txt")
        return tuple(paths)

    def read_answer(self) -> str | None:
        for path in self.answer_paths:
            try:
                text = path.read_text(encoding="utf-8").strip()
            except (OSError, UnicodeDecodeError):
                continue
            if text:
                return text
        return None


def load_task(root: str | Path) -> EvaluationTask:
    """Load one task directory."""
    root = Path(root)
    payload_path = root / "task.json"
    if not payload_path.is_file():
        raise FileNotFoundError(f"task.json not found in {root}")
    payload = json.loads(payload_path.read_text(encoding="utf-8"))

    expected = payload.get("expected")
    check = payload.get("check")
    solvable = payload.get("solvable")
    impossible = payload.get("impossible")
    return EvaluationTask(
        task_id=str(payload.get("task_id") or root.name),
        task_type=str(payload.get("task_type") or "unknown"),
        instruction=str(payload.get("instruction") or ""),
        reward=float(payload.get("reward") or 0),
        expected=None if expected is None else str(expected),
        check=None if check is None else str(check),
        root=root,
        solvable=not (solvable is False or impossible is True),
    )


def task_dataset_id(
    task: EvaluationTask,
    tasks_root: str | Path | None = None,
) -> str:
    """Task identifier used by the datasets: its path under ``data/task``.

    Example: ``coding/solvable/0001``.  This is different from the ``task_id``
    inside ``task.json`` (``coding_0003``), which is used by the harness.
    """
    tasks_root = Path(tasks_root) if tasks_root is not None else default_tasks_root()
    try:
        relative = task.root.resolve().relative_to(tasks_root.resolve())
        return relative.as_posix()
    except (OSError, ValueError):
        return task.task_id


def load_tasks_dir(tasks_dir: str | Path) -> list[EvaluationTask]:
    """Load every immediate child that contains a ``task.json``."""
    tasks_dir = Path(tasks_dir)
    if not tasks_dir.is_dir():
        raise FileNotFoundError(f"tasks directory not found: {tasks_dir}")
    tasks: list[EvaluationTask] = []
    for child in sorted(tasks_dir.iterdir()):
        if (child / "task.json").is_file():
            tasks.append(load_task(child))
    return tasks


@dataclass(frozen=True)
class TaskSetSpec:
    name: str
    random_seed: int | None
    task_paths: tuple[str, ...]
    source: Path


def load_task_set(path: str | Path) -> TaskSetSpec:
    """Load a ``data/task_set/*.yaml`` (or ``*.json``) specification.

    Supported YAML shape::

        dataset:
          random_seed: 42
          tasks:
            - coding/solvable/0001
            - data_analysis/solvable/0001

    ``tasks`` may also be an inline list: ``tasks: [coding/solvable/0001]``.
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        payload = json.loads(text)
    else:
        payload = _parse_task_set_yaml(text)

    dataset = payload.get("dataset", payload)
    if not isinstance(dataset, dict):
        raise ValueError(f"{path}: expected a mapping with a 'tasks' list")

    raw_tasks = dataset.get("tasks")
    if not isinstance(raw_tasks, list) or not raw_tasks:
        raise ValueError(f"{path}: 'tasks' must be a non-empty list")

    tasks = tuple(str(item).strip() for item in raw_tasks if str(item).strip())
    if not tasks:
        raise ValueError(f"{path}: 'tasks' list is empty")

    seed = dataset.get("random_seed")
    try:
        random_seed = None if seed is None else int(seed)
    except (TypeError, ValueError):
        raise ValueError(f"{path}: 'random_seed' must be an integer") from None

    return TaskSetSpec(
        name=path.stem,
        random_seed=random_seed,
        task_paths=tasks,
        source=path,
    )


def _parse_task_set_yaml(text: str) -> dict:
    """Parse the tiny YAML subset used by task-set files.

    We avoid a PyYAML dependency: task sets only contain a scalar
    ``random_seed`` and a list of task paths.
    """
    result: dict = {}
    lines = text.splitlines()
    for index, raw in enumerate(lines):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()
        indent = len(raw) - len(raw.lstrip(" "))

        if key == "random_seed":
            if value:
                result["random_seed"] = int(value)
            else:
                result["random_seed"] = None
            continue

        if key != "tasks":
            continue

        items: list[str] = []
        if value.startswith("[") and value.endswith("]"):
            items = [
                _unquote(item)
                for item in value[1:-1].split(",")
                if item.strip()
            ]
        elif value:
            items = [_unquote(value)]
        else:
            for next_line in lines[index + 1 :]:
                next_stripped = next_line.strip()
                if not next_stripped or next_stripped.startswith("#"):
                    continue
                next_indent = len(next_line) - len(next_line.lstrip(" "))
                if next_indent <= indent:
                    break
                if next_stripped.startswith("- "):
                    items.append(_unquote(next_stripped[2:].strip()))
        result["tasks"] = items

    return result


def _unquote(text: str) -> str:
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
        return text[1:-1]
    return text


def resolve_task_dir(raw: str | Path, tasks_root: str | Path | None = None) -> Path:
    """Resolve a task directory, a relative path or a ``task_id``.

    Resolution order:
    1. an existing path as given;
    2. a path relative to ``tasks_root`` (default ``data/task``);
    3. a path relative to the repository root;
    4. a directory whose ``task.json`` has the requested ``task_id``.
    """
    tasks_root = Path(tasks_root) if tasks_root is not None else default_tasks_root()
    raw_text = str(raw)
    candidate = Path(raw_text).expanduser()

    candidates = [candidate]
    if not candidate.is_absolute():
        candidates.append(tasks_root / candidate)
        candidates.append(repo_root() / candidate)
    for path in candidates:
        if (path / "task.json").is_file():
            return path.resolve()

    needle = raw_text.rstrip("/")
    if tasks_root.is_dir():
        for payload_path in tasks_root.rglob("task.json"):
            try:
                payload = json.loads(payload_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if str(payload.get("task_id") or payload_path.parent.name) == needle:
                return payload_path.parent.resolve()

    raise FileNotFoundError(f"cannot find task directory for {raw_text!r}")


def resolve_task_set(
    spec: TaskSetSpec,
    tasks_root: str | Path | None = None,
) -> list[EvaluationTask]:
    """Resolve the task paths of a set against ``tasks_root``."""
    tasks_root = Path(tasks_root) if tasks_root is not None else default_tasks_root()
    tasks: list[EvaluationTask] = []
    for raw in spec.task_paths:
        path = Path(raw)
        if not path.is_absolute():
            path = tasks_root / path
        if not (path / "task.json").is_file():
            # Be forgiving when the set is written relative to the repo root.
            alternative = repo_root() / raw
            if (alternative / "task.json").is_file():
                path = alternative
        tasks.append(load_task(path))
    return tasks


_IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__", ".mypy_cache", ".pytest_cache"}


def iter_test_files(workspace: str | Path) -> list[Path]:
    """Find ``test*.py`` files (the unittest-style check)."""
    workspace = Path(workspace)
    if not workspace.is_dir():
        return []
    found: list[Path] = []
    for path in workspace.rglob("test*.py"):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(workspace).parts
        if any(part in _IGNORED_DIRS for part in relative_parts):
            continue
        found.append(path.resolve())
    return sorted(found)


def snapshot_test_files(workspace: str | Path) -> dict[str, str]:
    """Hash test files so edits by the agent can be detected."""
    workspace = Path(workspace)
    snapshot: dict[str, str] = {}
    for path in iter_test_files(workspace):
        try:
            relative = path.relative_to(workspace.resolve())
            snapshot[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
        except (OSError, ValueError):
            continue
    return snapshot


def modified_test_files(
    workspace: str | Path,
    snapshot: dict[str, str],
) -> list[str]:
    """Return test files that were added, removed or changed."""
    current = snapshot_test_files(workspace)
    changed = set(snapshot) ^ set(current)
    changed.update(
        name
        for name in set(snapshot) & set(current)
        if snapshot[name] != current[name]
    )
    return sorted(changed)
