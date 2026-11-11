"""Prepare copies of tasks, run the harness and aggregate verdicts."""

from __future__ import annotations

import re
import shutil
import tempfile
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path

from evaluation.answer_evaluator import Verdict, evaluate_task
from evaluation.answer_evaluator.evaluator import HIDDEN_TESTS_DIR
from evaluation.common.cost import token_cost
from evaluation.common.runner import HarnessConfig, HarnessRun, run_harness
from evaluation.common.tasks import (
    EvaluationTask,
    load_task,
    modified_test_files,
    snapshot_test_files,
    task_dataset_id,
)


@dataclass
class PreparedSuite:
    base_dir: Path
    tasks_dir: Path
    tasks: tuple[EvaluationTask, ...]
    copied: dict[str, EvaluationTask]
    test_snapshots: dict[str, dict[str, str]]


@dataclass
class TaskOutcome:
    task: EvaluationTask
    verdict: Verdict
    solution: dict
    test_files_modified: list[str]

    @property
    def input_tokens(self) -> int:
        return _as_int(self.solution.get("input_tokens"))

    @property
    def output_tokens(self) -> int:
        return _as_int(self.solution.get("output_tokens"))

    @property
    def cost(self) -> int:
        raw_cost = self.solution.get("cost")
        if raw_cost is not None:
            return _as_int(raw_cost)
        return token_cost(self.input_tokens, self.output_tokens)

    @property
    def score(self) -> float:
        return self.task.reward if self.verdict.solved else 0.0


@dataclass(frozen=True)
class SuiteSummary:
    score: float
    max_score: float
    solved_tasks: int
    total_tasks: int
    input_tokens: int
    output_tokens: int
    cost: int

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "max_score": self.max_score,
            "solved_tasks": self.solved_tasks,
            "total_tasks": self.total_tasks,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost": self.cost,
        }


@dataclass
class SuiteRun:
    harness: HarnessRun
    outcomes: list[TaskOutcome]
    work_dir: Path | None


def prepare_suite(tasks: list[EvaluationTask], base_dir: str | Path) -> PreparedSuite:
    """Copy tasks into a flat directory that ``load_tasks`` can read.

    The harness expects ``<tasks-dir>/<task>/task.json``, while the dataset is
    nested (``coding/solvable/0001``).  Copies also protect the source dataset from
    edits made by the agent.
    """
    base_dir = Path(base_dir).resolve()
    tasks_dir = base_dir / "tasks"
    if tasks_dir.exists():
        shutil.rmtree(tasks_dir)
    tasks_dir.mkdir(parents=True, exist_ok=True)

    counts = Counter(task.task_id for task in tasks)
    duplicates = sorted(task_id for task_id, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError(f"duplicate task_id values in the set: {', '.join(duplicates)}")

    copied: dict[str, EvaluationTask] = {}
    snapshots: dict[str, dict[str, str]] = {}
    for index, task in enumerate(tasks):
        destination = tasks_dir / f"{index:03d}_{_safe_name(task.task_id)}"
        shutil.copytree(task.root, destination)
        for answer_path in (destination / "workspace" / "answer.txt", destination / "answer.txt"):
            answer_path.unlink(missing_ok=True)

        copied_task = load_task(destination)
        if copied_task.task_id != task.task_id:
            copied_task = replace(copied_task, task_id=task.task_id)
        copied[task.task_id] = copied_task

        check = (copied_task.check or "").strip().lower()
        if check == "unittest":
            snapshots[task.task_id] = snapshot_test_files(copied_task.workspace)
        elif check == "hidden_unittest":
            snapshots[task.task_id] = snapshot_test_files(
                copied_task.root / HIDDEN_TESTS_DIR
            )

    return PreparedSuite(
        base_dir=base_dir,
        tasks_dir=tasks_dir,
        tasks=tuple(tasks),
        copied=copied,
        test_snapshots=snapshots,
    )


def evaluate_suite(
    prepared: PreparedSuite,
    solutions: dict[str, dict],
    *,
    python: str | None,
    strict: bool = False,
    forbid_test_edits: bool = True,
) -> list[TaskOutcome]:
    """Turn the harness output into verdicts for the original task list."""
    outcomes: list[TaskOutcome] = []
    for task in prepared.tasks:
        copied_task = prepared.copied[task.task_id]
        solution = solutions.get(task.task_id, {})

        # The jury reads answer.txt, not solutions.json.  Do not silently fall
        # back to the JSON answer: a missing answer.txt is a harness bug.
        answer = copied_task.read_answer()

        verdict = evaluate_task(
            copied_task,
            answer=answer,
            python=python,
            strict=strict,
        )

        modified: list[str] = []
        check = (copied_task.check or "").strip().lower()
        if forbid_test_edits and check in {"unittest", "hidden_unittest"}:
            test_root = (
                copied_task.workspace
                if check == "unittest"
                else copied_task.root / HIDDEN_TESTS_DIR
            )
            modified = modified_test_files(
                test_root,
                prepared.test_snapshots.get(task.task_id, {}),
            )
            if modified:
                verdict = replace(
                    verdict,
                    solved=False,
                    detail=(
                        "tests were modified or removed: "
                        + ", ".join(modified)
                        + (f"; {verdict.detail}" if verdict.detail else "")
                    ),
                )

        outcomes.append(
            TaskOutcome(
                task=task,
                verdict=verdict,
                solution=solution,
                test_files_modified=modified,
            )
        )
    return outcomes


def summarize(outcomes: list[TaskOutcome]) -> SuiteSummary:
    return SuiteSummary(
        score=sum(outcome.score for outcome in outcomes),
        max_score=sum(outcome.task.reward for outcome in outcomes),
        solved_tasks=sum(1 for outcome in outcomes if outcome.verdict.solved),
        total_tasks=len(outcomes),
        input_tokens=sum(outcome.input_tokens for outcome in outcomes),
        output_tokens=sum(outcome.output_tokens for outcome in outcomes),
        cost=sum(outcome.cost for outcome in outcomes),
    )


def run_suite(
    tasks: list[EvaluationTask],
    config: HarnessConfig,
    *,
    python: str | None,
    strict: bool = False,
    forbid_test_edits: bool = True,
    work_dir: str | Path | None = None,
    keep: bool = False,
) -> SuiteRun:
    """Prepare copies, run the harness once and evaluate every task."""
    base_dir = (
        Path(work_dir).resolve()
        if work_dir is not None
        else Path(tempfile.mkdtemp(prefix="ojw-eval-"))
    )
    prepared = prepare_suite(tasks, base_dir)
    out_dir = base_dir / "out"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    try:
        harness = run_harness(
            config,
            prepared.tasks_dir,
            out_dir / "solutions.json",
        )
        outcomes = evaluate_suite(
            prepared,
            harness.solutions,
            python=python,
            strict=strict,
            forbid_test_edits=forbid_test_edits,
        )
    finally:
        if work_dir is None and not keep:
            shutil.rmtree(base_dir, ignore_errors=True)
            base_dir = None  # type: ignore[assignment]

    return SuiteRun(harness=harness, outcomes=outcomes, work_dir=base_dir)


def outcome_to_dict(outcome: TaskOutcome) -> dict:
    return {
        "task_id": outcome.task.task_id,
        "task_path": task_dataset_id(outcome.task),
        "task_type": outcome.task.task_type,
        "reward": outcome.task.reward,
        "check": outcome.task.check,
        "solvable": outcome.task.solvable,
        "solved": outcome.verdict.solved,
        "score": outcome.score,
        "verdict": outcome.verdict.to_dict(),
        "tokens": {
            "input": outcome.input_tokens,
            "output": outcome.output_tokens,
            "cost": outcome.cost,
        },
        "test_files_modified": outcome.test_files_modified,
    }


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._") or "task"


def _as_int(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
