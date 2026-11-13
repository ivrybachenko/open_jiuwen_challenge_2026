"""Harness entry point: solve tasks in two waves, persist after every attempt."""

from __future__ import annotations

import argparse
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

from harness.application.config import Settings
from harness.application.solutions import Solution, SolutionsStore
from harness.application.solver import BashAgentSolver, SolveResult, build_solver
from harness.application.tasks import Task, load_tasks

log = logging.getLogger("harness")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="run_agent.py")
    parser.add_argument("--tasks-dir", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument(
        "--budget",
        type=int,
        default=None,
        help="output-token budget; BUDGET is used when absent, then 100000.",
    )
    parser.add_argument("--model", default=None)
    parser.add_argument("--wave2-model", default=None,
                        help="model for the second wave; defaults to --model")
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Deprecated; kept for evaluator compatibility and ignored.",
    )
    parser.add_argument("--agent-workspace", type=Path, default=None)
    parser.add_argument(
        "--trajectories-dir",
        type=Path,
        default=None,
        help=(
            "Directory for attempt features; TRAJECTORIES_DIR is used when the "
            "flag is absent."
        ),
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help=(
            "Opaque evaluation run identifier stored in each attempt record; "
            "HARNESS_RUN_ID is used when the flag is absent."
        ),
    )
    parser.add_argument("--max-tasks", type=int, default=None)
    parser.add_argument("--wave1-max-tokens", type=int, default=None)
    parser.add_argument("--wave2-max-tokens", type=int, default=None)
    parser.add_argument("--wave2-max-tasks", type=int, default=None)
    parser.add_argument("--overview-max-tokens", type=int, default=None)
    parser.add_argument("--script-output-max-chars", type=int, default=None)
    parser.add_argument("--turn-timeout", type=float, default=None)
    parser.add_argument("--model-timeout", type=float, default=None)
    parser.add_argument(
        "--no-resume",
        dest="resume",
        action="store_false",
        default=None,
        help="Ignore saved per-task state and start every task from scratch.",
    )
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args(argv)


def _record(
    store: SolutionsStore,
    solver,
    task: Task,
    state,
    wave: str,
) -> SolveResult:
    result = solver.result_for(task, state)
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
            cost=result.cost,
            note=result.note,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
    )
    log.info(
        "task %s %s kind=%s solved=%s reward=%.0f cost=%d spent=%d total=%.0f",
        task.task_id,
        wave,
        result.answer_kind,
        result.solved,
        task.reward,
        result.cost,
        solver.spent,
        store.total_score,
    )
    return result


async def _run(args: argparse.Namespace) -> int:
    settings = Settings.from_env(
        tasks_dir=args.tasks_dir,
        out=args.out,
        budget=args.budget,
        model=args.model,
        wave2_model=args.wave2_model,
        max_iterations=args.max_iterations,
        agent_workspace=args.agent_workspace,
        trajectories_dir=args.trajectories_dir,
        run_id=args.run_id,
        wave1_max_tokens=args.wave1_max_tokens,
        wave2_max_tokens=args.wave2_max_tokens,
        wave2_max_tasks=args.wave2_max_tasks,
        overview_max_tokens=args.overview_max_tokens,
        script_output_max_chars=args.script_output_max_chars,
        turn_timeout=args.turn_timeout,
        model_timeout=args.model_timeout,
        resume=args.resume,
    )
    tasks = load_tasks(settings.tasks_dir)
    log.info(
        "loaded %d tasks from %s (model=%s, budget=%s, out=%s, trajectories=%s, "
        "run_id=%s, waves=%d/%d tokens)",
        len(tasks),
        settings.tasks_dir,
        settings.model,
        settings.budget,
        settings.out,
        settings.trajectories_dir,
        settings.run_id or "-",
        settings.wave1_max_tokens,
        settings.wave2_max_tokens,
    )

    store = SolutionsStore(settings.out)
    solver = build_solver(settings)
    if isinstance(solver, BashAgentSolver):
        solver.restore_budget(
            store.total_input_tokens,
            store.total_output_tokens,
            store.total_cost,
        )
    if args.max_tasks is not None:
        tasks = tasks[: args.max_tasks]

    try:
        await solver.start()
        states: dict[str, object] = {}
        log.info("wave 1: one turn per task")
        for task in tasks:
            if solver.ledger.exhausted:
                log.warning("token budget exhausted; stopping before %s", task.task_id)
                return 0
            if solver.abort_requested:
                log.warning("too many model errors; stopping before %s", task.task_id)
                return 0
            try:
                state = await solver.prepare(task)
            except Exception as exc:  # noqa: BLE001 - one task must not stop the run
                log.exception("cannot prepare %s", task.task_id)
                _record_crash(store, task, exc)
                continue
            states[task.task_id] = state

            if state.wave1_done:
                _record(store, solver, task, state, "wave1-resumed")
            else:
                try:
                    await solver.run_turn(task, state, 1)
                except Exception as exc:  # noqa: BLE001 - keep the run alive
                    log.exception("wave 1 crashed for %s", task.task_id)
                    solver.record_failure(task, state, 1, f"{type(exc).__name__}: {exc}")
                _record(store, solver, task, state, "wave1")

            if solver.budget_exceeded or solver.abort_requested:
                log.warning("stopping wave 1 after %s", task.task_id)
                break

        if solver.budget_exceeded or solver.abort_requested:
            log.warning("wave 2 skipped")
            return 0

        candidates = solver.select_wave2(tasks, states)
        log.info(
            "wave 2: %d promising task(s) selected (max %d)",
            len(candidates),
            settings.wave2_max_tasks,
        )
        for task, state in candidates:
            if solver.ledger.exhausted:
                log.warning("token budget exhausted; stopping before %s", task.task_id)
                break
            if solver.abort_requested:
                log.warning("too many model errors; stopping wave 2")
                break
            if state.wave2_done:
                continue
            try:
                await solver.run_turn(task, state, 2)
            except Exception as exc:  # noqa: BLE001 - keep the run alive
                log.exception("wave 2 crashed for %s", task.task_id)
                solver.record_failure(task, state, 2, f"{type(exc).__name__}: {exc}")
            _record(store, solver, task, state, "wave2")
            if solver.budget_exceeded or solver.abort_requested:
                log.warning("stopping wave 2 after %s", task.task_id)
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


def _record_crash(store: SolutionsStore, task: Task, exc: Exception) -> None:
    store.record(
        Solution(
            task_id=task.task_id,
            reward=task.reward,
            solved=False,
            answer=None,
            input_tokens=0,
            output_tokens=0,
            cost=0,
            note=f"solver crashed: {type(exc).__name__}: {exc}"[:500],
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=str(args.log_level).upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        return asyncio.run(_run(args))
    except KeyboardInterrupt:
        log.warning("interrupted")
        return 130
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        log.error("cannot start harness: %s", exc)
        return 2
    except Exception:  # noqa: BLE001 - save what was saved and exit cleanly
        log.exception("harness crashed")
        return 0
