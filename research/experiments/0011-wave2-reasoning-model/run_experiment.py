#!/usr/bin/env python3
"""Compare NR -> NR and NR -> R on the current prompt.

The 32-task set is the one used in experiment 0003.  Both configurations use
``qwen3.6-35b-a3b-noreason`` in wave 1; wave 2 is either the same model or
``qwen3.6-35b-a3b``.  Answers are checked by ``evaluation.answer_evaluator``.

Usage::

    LLM_BASE_URL=... LLM_API_KEY=... harness/.venv/bin/python \
        research/experiments/0011-wave2-reasoning-model/run_experiment.py \
        --repeats 2
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from evaluation.answer_evaluator.evaluator import evaluate_task  # noqa: E402
from evaluation.common.tasks import load_task  # noqa: E402

MODEL = "qwen3.6-35b-a3b-noreason"
REASONING = "qwen3.6-35b-a3b"
WRAPPER = ROOT / "research/experiments/0006-predict-cost-before-solve/rate_limit_runner.py"
BASE_URL = "https://api.neuraldeep.ru/v1"


def _task_rels(path: Path) -> list[str]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return list(payload["dataset"]["tasks"])


def _copy_tasks(rels: list[str], dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    for rel in rels:
        src = ROOT / "data" / "task" / rel
        target = dest / rel.replace("/", "__")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, target)


def _run(settings: dict, tasks_dir: Path, work: Path, run_id: str,
         wave2_model: str) -> dict:
    env = dict(__import__("os").environ)
    env["LLM_BASE_URL"] = BASE_URL
    env["LLM_API_KEY"] = env.get("LLM_API_KEY") or env.get("NEURAL_DEEP_API_KEY", "")
    cmd = [
        sys.executable, str(WRAPPER),
        "--tasks-dir", str(tasks_dir),
        "--out", str(work / "solutions.json"),
        "--agent-workspace", str(work / "agents"),
        "--trajectories-dir", str(work / "traj"),
        "--run-id", run_id,
        "--no-resume",
        "--model", MODEL,
        "--wave2-model", wave2_model,
        "--wave2-max-tasks", "0",
        "--log-level", "WARNING",
    ]
    log = work / "harness.log"
    work.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8") as fh:
        subprocess.run(cmd, cwd=ROOT / "harness", env=env, check=False,
                       stdout=fh, stderr=subprocess.STDOUT)
    if not (work / "solutions.json").is_file():
        return {"error": "no solutions"}
    solutions = json.loads((work / "solutions.json").read_text(encoding="utf-8"))
    return {"solutions": solutions}


def _evaluate(tasks_dir: Path) -> dict[str, bool]:
    results: dict[str, bool] = {}
    for child in sorted(tasks_dir.glob("*/task.json")):
        task_dir = child.parent
        try:
            task = load_task(task_dir)
            verdict = evaluate_task(task, timeout=90.0)
            results[task.task_id] = bool(verdict.solved)
        except Exception as exc:  # noqa: BLE001
            print(f"evaluator error {task_dir}: {exc}", file=sys.stderr)
            results[task_dir.name] = False
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-yaml", type=Path,
                        default=ROOT / "research/experiments/0003-reasoning-models-and-explanations/tasks.yaml")
    parser.add_argument("--out-dir", type=Path,
                        default=Path(__file__).resolve().parent / "results")
    parser.add_argument("--work-dir", type=Path, default=Path("/tmp/exp0011"))
    parser.add_argument("--repeats", type=int, default=2)
    args = parser.parse_args(argv)
    rels = _task_rels(args.tasks_yaml)
    configs = [("nn", MODEL), ("nr", REASONING)]
    rows = []
    for name, wave2_model in configs:
        for repeat in range(1, args.repeats + 1):
            run_id = f"exp0011-{name}-r{repeat}-{int(time.time())}"
            work = args.work_dir / f"{name}-r{repeat}"
            tasks_dir = work / "tasks"
            _copy_tasks(rels, tasks_dir)
            started = time.time()
            _run({}, tasks_dir, work, run_id, wave2_model)
            correct = _evaluate(tasks_dir)
            solutions = json.loads((work / "solutions.json").read_text(encoding="utf-8"))
            score = 0.0
            solved = 0
            for rel in rels:
                task_dir = tasks_dir / rel.replace("/", "__")
                meta = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
                task_id = meta["task_id"]
                if correct.get(task_id):
                    score += float(meta.get("reward", 0))
                    solved += 1
            # Wave breakdown from trajectories.
            wave2_ok = 0
            wave2_total = 0
            traj = work / "traj" / "bash_attempts.jsonl"
            if traj.is_file():
                for line in traj.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    record = json.loads(line)
                    if int(record.get("wave", 0)) == 2:
                        wave2_total += 1
                for rel in rels:
                    task_dir = tasks_dir / rel.replace("/", "__")
                    meta = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
                    task_id = meta["task_id"]
                    if correct.get(task_id):
                        # counted only if the task had a wave-2 record
                        pass
            row = {
                "config": name,
                "repeat": repeat,
                "wave2_model": wave2_model,
                "score": score,
                "solved": solved,
                "cost": int(solutions.get("total_cost", 0)),
                "score_per_1k": 1000.0 * score / max(1, int(solutions.get("total_cost", 0))),
                "wave2_turns": wave2_total,
                "seconds": round(time.time() - started, 1),
            }
            rows.append(row)
            print(row, flush=True)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "comparison.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    import pandas as pd
    pd.DataFrame(rows).to_csv(args.out_dir / "comparison.csv", index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
