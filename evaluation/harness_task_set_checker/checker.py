"""Check whether the harness solves a set of tasks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from evaluation.common.reporting import tail
from evaluation.common.runner import HarnessConfig
from evaluation.common.suite import (
    SuiteSummary,
    TaskOutcome,
    outcome_to_dict,
    run_suite,
    summarize,
)
from evaluation.common.tasks import TaskSetSpec


@dataclass
class TaskSetCheckReport:
    spec: TaskSetSpec
    outcomes: list[TaskOutcome]
    summary: SuiteSummary
    harness_command: list[str]
    harness_returncode: int
    harness_timed_out: bool
    harness_duration_seconds: float
    harness_stdout: str
    harness_stderr: str
    work_dir: Path | None

    def to_dict(self) -> dict:
        return {
            "task_set": self.spec.name,
            "source": str(self.spec.source),
            "random_seed": self.spec.random_seed,
            "summary": self.summary.to_dict(),
            "time_seconds": round(self.harness_duration_seconds, 3),
            "time_minutes": round(self.harness_duration_seconds / 60.0, 3),
            "harness": {
                "command": self.harness_command,
                "returncode": self.harness_returncode,
                "timed_out": self.harness_timed_out,
                "stdout_tail": tail(self.harness_stdout),
                "stderr_tail": tail(self.harness_stderr),
            },
            "tasks": [outcome_to_dict(outcome) for outcome in self.outcomes],
            "work_dir": str(self.work_dir) if self.work_dir else None,
        }


def check_task_set(
    spec: TaskSetSpec,
    tasks,
    config: HarnessConfig,
    *,
    python: str | None,
    strict: bool = False,
    forbid_test_edits: bool = True,
    max_tasks: int | None = None,
    keep: bool = False,
) -> TaskSetCheckReport:
    selected = list(tasks)
    if max_tasks is not None:
        selected = selected[:max_tasks]

    suite = run_suite(
        selected,
        config,
        python=python,
        strict=strict,
        forbid_test_edits=forbid_test_edits,
        keep=keep,
    )
    return TaskSetCheckReport(
        spec=spec,
        outcomes=suite.outcomes,
        summary=summarize(suite.outcomes),
        harness_command=suite.harness.command,
        harness_returncode=suite.harness.returncode,
        harness_timed_out=suite.harness.timed_out,
        harness_duration_seconds=suite.harness.duration_seconds,
        harness_stdout=suite.harness.stdout,
        harness_stderr=suite.harness.stderr,
        work_dir=suite.work_dir,
    )
