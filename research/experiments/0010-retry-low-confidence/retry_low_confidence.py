#!/usr/bin/env python3
"""Retry answered tasks with low predicted success.

The current harness never retries a task that produced a non-empty
``answer.txt``.  The online model from experiment 0007 identifies answered
tasks with very low ``P(correct)``.  This experiment takes the lowest-confidence
answered tasks from the fresh run, deletes the old answer, asks for one more
turn with an explicit "your previous answer may be wrong" warning, and
evaluates the new answer.

It is a research runner: the shipped harness is not modified.

Usage::

    LLM_API_KEY="$NEURAL_DEEP_API_KEY" harness/.venv/bin/python \
        research/experiments/0010-retry-low-confidence/retry_low_confidence.py \
        --limit 20
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "harness" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "harness" / "src"))

from evaluation.answer_evaluator.evaluator import evaluate_task  # noqa: E402
from harness.application.config import Settings  # noqa: E402
from harness.application.solver import BashAgentSolver  # noqa: E402
from harness.application.tasks import Task, load_tasks  # noqa: E402


class RetrySolver(BashAgentSolver):
    @staticmethod
    def _wave2_warning(state) -> str:  # noqa: ANN001
        kind = state.answer_kind
        return (
            "The previous attempt produced an answer "
            f"(kind={kind}), but it may be wrong. Re-check the task from the "
            "current workspace state. If the answer is correct, keep it; "
            "otherwise compute a new answer and overwrite answer.txt. Reply "
            "with one bash script and nothing else."
        )


def _copy_and_rewrite(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    old = str(source)
    new = str(target)
    for path in target.rglob("state.json"):
        path.write_text(path.read_text(encoding="utf-8").replace(old, new),
                        encoding="utf-8")


def _find_task(tasks_dir: Path, task_id: str) -> Task | None:
    for task in load_tasks(tasks_dir):
        if task.task_id == task_id:
            return task
    return None


async def _run_one(
    solver: RetrySolver,
    shard_dir: Path,
    task_id: str,
    old_cost: float,
    old_correct: bool,
    probability: float,
) -> dict[str, Any]:
    tasks = load_tasks(shard_dir / "tasks")
    task = next((t for t in tasks if t.task_id == task_id), None)
    if task is None:
        return {"task_id": task_id, "error": "task not found"}
    state = await solver.prepare(task)
    if not state.wave1_done or not state.turns:
        return {"task_id": task_id, "error": "wave1 state not loaded"}
    if state.wave2_done:
        return {"task_id": task_id, "error": "wave2 already done"}
    solver._prepare_wave2(task, state)
    turn = await solver.run_turn(task, state, 2)
    result = solver.result_for(task, state)
    if result.answer is not None:
        task.write_answer(result.answer)
    try:
        verdict = evaluate_task(task, timeout=90.0)
        new_correct = bool(verdict.solved)
        detail = verdict.detail
    except Exception as exc:  # noqa: BLE001
        new_correct = False
        detail = f"{type(exc).__name__}: {exc}"
    return {
        "task_id": task_id,
        "probability": probability,
        "old_cost": old_cost,
        "old_correct": old_correct,
        "new_cost_total": result.cost,
        "new_cost_turn": max(0.0, result.cost - old_cost),
        "new_correct": new_correct,
        "new_answer_kind": result.answer_kind,
        "detail": detail,
        "model_error": (turn or {}).get("model_error", ""),
    }


async def main_async(args: argparse.Namespace) -> int:
    source = args.work_root / f"rep{args.rep}"
    target = args.out_root
    _copy_and_rewrite(source, target)
    all_agents = target / "all_agents"
    if all_agents.exists():
        shutil.rmtree(all_agents)
    all_agents.mkdir(parents=True)
    for shard in sorted(target.glob("shard*")):
        for agent in (shard / "work" / "agents").glob("*"):
            shutil.copytree(agent, all_agents / agent.name)
    policy = __import__("pandas").read_csv(args.policy)
    policy = policy[policy["source"].str.startswith("fresh")].copy()
    policy = policy[policy["answered"] == 1].sort_values("prob_correct")
    if args.only_solvable_wrong:
        policy = policy[(policy["correct"] == 0) & (policy["impossible_label"] == 0)]
    policy = policy.head(args.limit)
    rows: list[dict[str, Any]] = []
    settings = Settings.from_env(
        tasks_dir=target,
        out=target / "retry_solutions.json",
        model=args.model,
        agent_workspace=all_agents,
        trajectories_dir=target / "traj",
        run_id=f"retry0010-{int(time.time())}",
        resume=True,
    )
    solver = RetrySolver(settings)
    await solver.start()
    try:
        for index, (_, row) in enumerate(policy.iterrows(), start=1):
            task_id = row["task_id"]
            source_name = str(row["source"])
            shard_name = source_name.split("/")[1] if "/" in source_name else "shard0"
            shard_dir = target / shard_name
            try:
                result = await asyncio.wait_for(
                    _run_one(
                        solver, shard_dir, task_id, float(row["cost"]),
                        bool(row["correct"]), float(row["prob_correct"]),
                    ),
                    timeout=args.task_timeout,
                )
            except asyncio.TimeoutError:
                result = {"task_id": task_id, "error": "timeout"}
            rows.append(result)
            print(f"{index}/{len(policy)} {task_id} prob={row['prob_correct']:.3f} "
                  f"old={row['correct']} new={result.get('new_correct')} "
                  f"cost+={result.get('new_cost_turn', 0):.0f}", flush=True)
            await asyncio.sleep(0.5)
    finally:
        await solver.close()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    import pandas as pd
    pd.DataFrame(rows).to_csv(args.out_dir / "retry_results.csv", index=False)
    fixed = sum(1 for row in rows if row.get("new_correct") and not row.get("old_correct"))
    spent = sum(float(row.get("new_cost_turn", 0)) for row in rows)
    print(f"fixed {fixed}/{len(rows)}; extra tokens {spent:.0f}", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path,
                        default=ROOT / "research/experiments/0007-predict-remaining-cost-during-solve/results/policy_tasks.csv")
    parser.add_argument("--work-root", type=Path, default=Path("/tmp/pred0006"))
    parser.add_argument("--out-root", type=Path, default=Path("/tmp/retry0006"))
    parser.add_argument("--out-dir", type=Path,
                        default=Path(__file__).resolve().parent / "results")
    parser.add_argument("--rep", type=int, default=100)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--only-solvable-wrong", action="store_true")
    parser.add_argument("--task-timeout", type=float, default=90.0)
    parser.add_argument("--model", default="qwen3.6-35b-a3b-noreason")
    args = parser.parse_args(argv)
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
