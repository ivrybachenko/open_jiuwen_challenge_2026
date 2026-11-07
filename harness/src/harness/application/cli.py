"""Harness entry point: load tasks, solve them, persist after each task."""

from __future__ import annotations

import argparse
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

from harness.application.config import Settings
from harness.application.llm import BudgetExceeded, token_cost
from harness.application.solutions import Solution, SolutionsStore
from harness.application.solver import SolveResult, build_solver
from harness.application.tasks import load_tasks

log = logging.getLogger("harness")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="run_agent.py")
    parser.add_argument("--tasks-dir", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--budget", type=int, default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-iterations", type=int, default=None)
    parser.add_argument("--agent-workspace", type=Path, default=None)
    parser.add_argument("--max-tasks", type=int, default=None)
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args(argv)


async def _run(args: argparse.Namespace) -> int:
    settings = Settings.from_env(
        tasks_dir=args.tasks_dir,
        out=args.out,
        budget=args.budget,
        model=args.model,
        max_iterations=args.max_iterations,
        agent_workspace=args.agent_workspace,
    )
    tasks = load_tasks(settings.tasks_dir)
    log.info(
        "loaded %d tasks from %s (model=%s, budget=%s, out=%s)",
        len(tasks),
        settings.tasks_dir,
        settings.model,
        settings.budget,
        settings.out,
    )

    store = SolutionsStore(settings.out)
    solver = build_solver(settings)
    if args.max_tasks is not None:
        tasks = tasks[: args.max_tasks]

    await solver.start()
    budget_exceeded = False
    try:
        for task in tasks:
            if solver.ledger.exhausted:
                log.warning("token budget exhausted; stopping")
                break

            try:
                result = await solver.solve(task)
            except Exception:  # noqa: BLE001 - one broken task must not stop the run
                log.exception("task %s failed", task.task_id)
                result = SolveResult(note="solver crashed")

            if result.answer is not None:
                try:
                    task.write_answer(result.answer)
                except OSError:
                    log.exception("cannot write answer.txt for %s", task.task_id)

            task_cost = token_cost(result.input_tokens, result.output_tokens)
            try:
                solver.ledger.charge(result.input_tokens, result.output_tokens)
            except BudgetExceeded:
                budget_exceeded = True
                log.warning("token budget exceeded after %s", task.task_id)

            store.record(
                Solution(
                    task_id=task.task_id,
                    reward=task.reward,
                    solved=result.solved,
                    answer=result.answer,
                    input_tokens=result.input_tokens,
                    output_tokens=result.output_tokens,
                    cost=task_cost,
                    note=result.note,
                    updated_at=datetime.now(timezone.utc).isoformat(),
                )
            )
            log.info(
                "task %s solved=%s reward=%.0f cost=%d spent=%d total=%.0f",
                task.task_id,
                result.solved,
                task.reward,
                task_cost,
                solver.spent,
                store.total_score,
            )

            if budget_exceeded:
                break
    finally:
        await solver.close()

    log.info(
        "done: score=%.0f spent=%d solutions=%s",
        store.total_score,
        solver.spent,
        store.path,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    return asyncio.run(_run(args))
