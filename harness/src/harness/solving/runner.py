"""Harness run orchestration.

The CLI only parses arguments; this module owns setup, the task loop,
solutions persistence and crash isolation.  Which tasks get the next wave is
decided by :mod:`harness.solving.scheduler`.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

from harness.solving.agents.script_agent import ScriptAgent, SolveResult
from harness.config import Settings
from harness.accounting import Solution, SolutionsStore
from harness.solving.scheduler import WaveScheduler
from harness.tasks import TaskState
from harness.tasks import Task, load_tasks

log = logging.getLogger("harness")


def _record(
    store: SolutionsStore,
    agent: ScriptAgent,
    task: Task,
    state: TaskState,
    wave: str,
) -> SolveResult:
    result = agent.result_for(task, state)
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
        agent.spent,
        store.total_score,
    )
    return result


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
        max_waves=args.max_waves,
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

    # OUT may be set but not mounted (the run command in the regulation does
    # not mount it).  Keep the run alive: fall back to the writable tasks mount
    # and then to the tmpfs copy.
    store = SolutionsStore(
        settings.out,
        fallbacks=(
            settings.tasks_dir / "solutions.json",
            Path("/tmp/solutions.json"),
        ),
    )
    agent = ScriptAgent(settings)
    agent.restore_budget(
        store.total_input_tokens,
        store.total_output_tokens,
        store.total_cost,
    )
    scheduler = WaveScheduler(settings)
    if args.max_tasks is not None:
        tasks = tasks[: args.max_tasks]

    try:
        await agent.start()
        states: dict[str, TaskState] = {}
        log.info("wave 1: one turn per task")
        for task in tasks:
            if agent.ledger.exhausted:
                log.warning("token budget exhausted; stopping before %s", task.task_id)
                return 0
            if agent.abort_requested:
                log.warning("too many model errors; stopping before %s", task.task_id)
                return 0
            try:
                state = await agent.prepare(task)
            except Exception as exc:  # noqa: BLE001 - one task must not stop the run
                log.exception("cannot prepare %s", task.task_id)
                _record_crash(store, task, exc)
                continue
            states[task.task_id] = state

            if state.wave1_done:
                _record(store, agent, task, state, "wave1-resumed")
            else:
                try:
                    await agent.invoke({"task": task, "state": state, "wave": 1})
                except Exception as exc:  # noqa: BLE001 - keep the run alive
                    log.exception("wave 1 crashed for %s", task.task_id)
                    agent.record_failure(task, state, 1, f"{type(exc).__name__}: {exc}")
                _record(store, agent, task, state, "wave1")

            if agent.budget_exceeded or agent.abort_requested:
                log.warning("stopping wave 1 after %s", task.task_id)
                break

        for wave in range(2, settings.max_waves + 1):
            if agent.budget_exceeded or agent.abort_requested:
                log.warning("wave %d skipped", wave)
                return 0

            candidates = scheduler.select_candidates(
                tasks,
                states,
                wave,
                remaining=agent.ledger.remaining,
            )
            log.info(
                "wave %d: %d promising task(s) selected (max %d)",
                wave,
                len(candidates),
                settings.wave2_max_tasks,
            )
            if not candidates:
                break
            for task, state in candidates:
                if agent.ledger.exhausted:
                    log.warning(
                        "token budget exhausted; stopping before %s", task.task_id
                    )
                    break
                if agent.abort_requested:
                    log.warning("too many model errors; stopping wave %d", wave)
                    break
                try:
                    await agent.invoke(
                        {"task": task, "state": state, "wave": wave}
                    )
                except Exception as exc:  # noqa: BLE001 - keep the run alive
                    log.exception("wave %d crashed for %s", wave, task.task_id)
                    agent.record_failure(
                        task, state, wave, f"{type(exc).__name__}: {exc}"
                    )
                _record(store, agent, task, state, f"wave{wave}")
                if agent.budget_exceeded or agent.abort_requested:
                    log.warning("stopping wave %d after %s", wave, task.task_id)
                    break
    finally:
        await agent.close()

    log.info(
        "done: score=%.0f spent=%d solutions=%s",
        store.total_score,
        agent.spent,
        store.path,
    )
    return 0


def run(args: argparse.Namespace) -> int:
    """Run the harness for parsed CLI arguments."""
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
