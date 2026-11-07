"""Check whether the harness solves a single task."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from evaluation.common.reporting import tail
from evaluation.common.runner import HarnessConfig
from evaluation.common.suite import TaskOutcome, outcome_to_dict, run_suite
from evaluation.common.tasks import EvaluationTask, task_dataset_id


@dataclass
class TaskCheckReport:
    task: EvaluationTask
    outcome: TaskOutcome
    harness_command: list[str]
    harness_returncode: int
    harness_timed_out: bool
    harness_duration_seconds: float
    harness_stdout: str
    harness_stderr: str
    work_dir: Path | None

    @property
    def solved(self) -> bool:
        return self.outcome.verdict.solved

    def to_dict(self) -> dict:
        payload = outcome_to_dict(self.outcome)
        payload.update(
            {
                "task_path": task_dataset_id(self.task),
                "score": self.outcome.score,
                "time_seconds": round(self.harness_duration_seconds, 3),
                "time_minutes": round(self.harness_duration_seconds / 60.0, 3),
                "harness": {
                    "command": self.harness_command,
                    "returncode": self.harness_returncode,
                    "timed_out": self.harness_timed_out,
                    "stdout_tail": tail(self.harness_stdout),
                    "stderr_tail": tail(self.harness_stderr),
                },
                "work_dir": str(self.work_dir) if self.work_dir else None,
            }
        )
        return payload


def check_task(
    task: EvaluationTask,
    config: HarnessConfig,
    *,
    python: str | None,
    strict: bool = False,
    forbid_test_edits: bool = True,
    keep: bool = False,
) -> TaskCheckReport:
    suite = run_suite(
        [task],
        config,
        python=python,
        strict=strict,
        forbid_test_edits=forbid_test_edits,
        keep=keep,
    )
    outcome = suite.outcomes[0]
    return TaskCheckReport(
        task=task,
        outcome=outcome,
        harness_command=suite.harness.command,
        harness_returncode=suite.harness.returncode,
        harness_timed_out=suite.harness.timed_out,
        harness_duration_seconds=suite.harness.duration_seconds,
        harness_stdout=suite.harness.stdout,
        harness_stderr=suite.harness.stderr,
        work_dir=suite.work_dir,
    )
