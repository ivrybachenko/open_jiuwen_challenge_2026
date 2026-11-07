"""Harness entry point: load tasks, solve them, persist after each task."""

from __future__ import annotations

import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path

from .config import Settings
from .solutions import Solution, SolutionsStore
from .solver import SolveResult, build_solver
from .tasks import load_tasks

log = logging.getLogger("harness")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="run_agent.py")
    parser.add_argument("--tasks-dir", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--budget", type=int, default=None)
    parser.add_argument("--max-tasks", type=int, default=None)
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    settings = Settings.from_env(
        tasks_dir=args.tasks_dir, out=args.out, budget=args.budget
    )
    tasks = load_tasks(settings.tasks_dir)
    log.info(
        "loaded %d tasks from %s (budget=%s, out=%s)",
        len(tasks),
        settings.tasks_dir,
        settings.budget,
        settings.out,
    )

    store = SolutionsStore(settings.out)
    solver = build_solver(settings)
    if args.max_tasks is not None:
        tasks = tasks[: args.max_tasks]

    for task in tasks:
        if solver.ledger.exhausted:
            log.warning("token budget exhausted; stopping")
            break

        try:
            result = solver.solve(task)
        except Exception:  # noqa: BLE001 - one broken task must not stop the run
            log.exception("task %s failed", task.task_id)
            result = SolveResult(note="solver crashed")

        if result.answer is not None:
            try:
                task.write_answer(result.answer)
            except OSError:
                log.exception("cannot write answer.txt for %s", task.task_id)

        store.record(
            Solution(
                task_id=task.task_id,
                reward=task.reward,
                solved=result.solved,
                answer=result.answer,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                cost=solver.spent,
                note=result.note,
                updated_at=datetime.now(timezone.utc).isoformat(),
            )
        )
        log.info(
            "task %s solved=%s reward=%.0f spent=%d total=%.0f",
            task.task_id,
            result.solved,
            task.reward,
            solver.spent,
            store.total_score,
        )

    log.info(
        "done: score=%.0f spent=%d solutions=%s",
        store.total_score,
        solver.spent,
        store.path,
    )
    return 0
