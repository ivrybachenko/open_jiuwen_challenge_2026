"""Helpers for the solvable-task generator.

The generator writes ``data/task/<category>/solvable/<NNNN>`` directories.  Code
tasks are verified twice: the shipped starter must fail, and the reference
implementation must pass.  Exact-answer tasks receive the answer computed from
the generated data, not a hand-typed value.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TASKS_ROOT = REPO_ROOT / "data" / "task"
GENERATED_INDICES = range(7, 41)


def task_root(category: str, index: int) -> Path:
    return TASKS_ROOT / category / "solvable" / f"{index:04d}"


def _write_files(base: Path, files: dict[str, str]) -> None:
    for relative, content in files.items():
        path = base / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _run_test_file(path: Path, workspace: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    previous = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        str(workspace) if not previous else str(workspace) + os.pathsep + previous
    )
    return subprocess.run(
        [sys.executable, str(path)],
        cwd=str(workspace),
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )


def _test_files(workspace: Path, hidden_tests: dict[str, str] | None) -> list[Path]:
    base = workspace if hidden_tests is None else workspace.parent / "tests"
    return sorted(base.rglob("test*.py"))


def _verify_code_task(
    workspace: Path,
    hidden_tests: dict[str, str] | None,
    reference: dict[str, str],
    baseline_should_fail: bool = True,
) -> None:
    with tempfile.TemporaryDirectory(prefix="task-check-") as tmp:
        base = Path(tmp)
        work = base / "workspace"
        shutil.copytree(workspace, work)
        if hidden_tests:
            _write_files(base, hidden_tests)

        tests = _test_files(work, hidden_tests)
        if not tests:
            raise AssertionError(f"no tests for {workspace}")
        baseline = [_run_test_file(path, work) for path in tests]
        if baseline_should_fail and all(item.returncode == 0 for item in baseline):
            raise AssertionError(f"starter already passes tests: {workspace}")

        _write_files(work, reference)
        for cache in work.rglob("__pycache__"):
            shutil.rmtree(cache, ignore_errors=True)
        solved = [_run_test_file(path, work) for path in tests]
        failed = [item for item in solved if item.returncode != 0]
        if failed:
            details = "\n\n".join(
                ((item.stdout or "") + (item.stderr or ""))[-3000:] for item in failed
            )
            raise AssertionError(f"reference fails tests for {workspace}:\n{details}")


def _verify_exact_task(expected: str) -> None:
    if expected is None or not str(expected).strip():
        raise AssertionError("empty expected answer")


def create_task(
    *,
    category: str,
    index: int,
    task_id: str,
    instruction: str,
    reward: int,
    check: str,
    expected: str,
    workspace: dict[str, str] | None = None,
    hidden_tests: dict[str, str] | None = None,
    reference: dict[str, str] | None = None,
) -> Path:
    root = task_root(category, index)
    if root.exists():
        shutil.rmtree(root)
    (root / "workspace").mkdir(parents=True)

    payload = {
        "task_id": task_id,
        "task_type": category,
        "instruction": instruction,
        "reward": reward,
        "expected": str(expected),
        "check": check,
    }
    (root / "task.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    files = dict(workspace or {})
    _write_files(root / "workspace", files)
    if hidden_tests:
        _write_files(root, hidden_tests)

    if check in {"unittest", "hidden_unittest"}:
        if reference is None:
            raise AssertionError(f"{task_id}: code task without reference")
        _verify_code_task(root / "workspace", hidden_tests, reference)
    else:
        _verify_exact_task(str(expected))
    return root


def csv_text(header: list[str], rows: list[list[object]], delimiter: str = ",") -> str:
    lines = [delimiter.join(header)]
    for row in rows:
        lines.append(delimiter.join(str(value) for value in row))
    return "\n".join(lines) + "\n"


def jsonl_text(rows: list[dict]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)


def clean_generated_indices(category: str) -> None:
    for index in GENERATED_INDICES:
        path = task_root(category, index)
        if path.exists():
            shutil.rmtree(path)
