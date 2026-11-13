#!/usr/bin/env python3
"""Collect current-harness costs for the static predictor.

The harness mutates task workspaces (answers, code edits), so every repeat
runs on a fresh copy.  Tasks are split into shards and the shards run in
parallel; the LLM proxy allows up to five concurrent sessions.

Outputs:

* ``results/current_runs.csv`` -- one row per (task, repeat), with total and
  per-wave cost, number of turns and evaluator correctness;
* ``results/correctness_repN.json`` -- raw evaluator map;
* ``results/collection.json`` -- command lines, model and counts.

Usage::

    LLM_API_KEY="$NEURAL_DEEP_API_KEY" harness/.venv/bin/python \
        research/experiments/0006-predict-cost-before-solve/collect_costs.py \
        --reps 2 --shards 5
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.answer_evaluator.evaluator import evaluate_task  # noqa: E402
from evaluation.common.tasks import load_task  # noqa: E402

DEFAULT_TASKS = ROOT / "data" / "task"
DEFAULT_EXAMPLES = ROOT / "challenge_info" / "task-examples"
DEFAULT_WORK = Path("/tmp/pred0006")
BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.neuraldeep.ru/v1")
WRAPPER = Path(__file__).resolve().parent / "rate_limit_runner.py"


def _api_key() -> str:
    key = os.environ.get("LLM_API_KEY") or os.environ.get("NEURAL_DEEP_API_KEY")
    if not key:
        raise SystemExit("LLM_API_KEY or NEURAL_DEEP_API_KEY must be set")
    return key


def _id_to_rel() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for tj in (ROOT / "data" / "task").glob("*/*/*/task.json"):
        try:
            meta = json.loads(tj.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        mapping[meta.get("task_id", "")] = "/".join(tj.parts[-4:-1])
    return mapping


ID_TO_REL = _id_to_rel()


def _source_rel(directory: Path) -> str:
    try:
        meta = json.loads((directory / "task.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return directory.name
    return ID_TO_REL.get(meta.get("task_id", ""), directory.name)


def _task_dirs(root: Path) -> list[Path]:
    return sorted(p.parent for p in root.glob("*/[!.]*/[!.]*/task.json"))


def _copy_tasks(task_dirs: list[Path], dest: Path) -> list[Path]:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    copied = []
    for src in task_dirs:
        target = dest / src.name
        # Keep the category/name in the directory name to avoid collisions.
        target = dest / f"{src.parts[-3]}__{src.parts[-2]}__{src.parts[-1]}"
        shutil.copytree(src, target)
        copied.append(target)
    return copied


def _run_harness(
    tasks_dir: Path,
    out: Path,
    work: Path,
    run_id: str,
    model: str,
    log_path: Path,
    wave2_max_tasks: int,
) -> subprocess.Popen[Any]:
    env = dict(os.environ)
    env["LLM_BASE_URL"] = BASE_URL
    env["LLM_API_KEY"] = _api_key()
    cmd = [
        sys.executable,
        str(WRAPPER),
        "--tasks-dir",
        str(tasks_dir),
        "--out",
        str(out),
        "--agent-workspace",
        str(work / "agents"),
        "--trajectories-dir",
        str(work / "traj"),
        "--run-id",
        run_id,
        "--no-resume",
        "--model",
        model,
        "--wave2-max-tasks",
        str(wave2_max_tasks),
        "--log-level",
        "WARNING",
    ]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log = log_path.open("w", encoding="utf-8")
    return subprocess.Popen(cmd, cwd=ROOT / "harness", env=env,
                            stdout=log, stderr=subprocess.STDOUT)


def _evaluate(tasks_dir: Path, out: Path) -> dict[str, bool]:
    results: dict[str, bool] = {}
    for child in sorted(tasks_dir.iterdir()):
        if not (child / "task.json").is_file():
            continue
        try:
            task = load_task(child)
            verdict = evaluate_task(task, timeout=90.0)
            results[task.task_id] = bool(verdict.solved)
        except Exception as exc:  # noqa: BLE001
            results[child.name] = False
            print(f"evaluator error for {child.name}: {exc}", file=sys.stderr)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True),
                   encoding="utf-8")
    return results


def _turn_costs(traj_path: Path) -> dict[tuple[str, int], list[int]]:
    """(run_id, task_id) -> costs of each turn, in order."""
    by_turn: dict[tuple[str, int], list[tuple[int, int]]] = {}
    for line in traj_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        cost = int(record["output_tokens"]) + math.ceil(
            int(record["input_tokens"]) / 10
        )
        key = (record["run_id"], record["task_id"])
        by_turn.setdefault(key, []).append((int(record["wave"]), cost))
    return {
        key: [cost for _, cost in sorted(values)]
        for key, values in by_turn.items()
    }


def _collect_rep(
    rep: int,
    task_dirs: list[Path],
    shards: int,
    work_root: Path,
    model: str,
    wave2_max_tasks: int,
) -> list[dict[str, Any]]:
    rep_dir = work_root / f"rep{rep}"
    rep_dir.mkdir(parents=True, exist_ok=True)
    shard_sets = [task_dirs[i::shards] for i in range(shards)]
    processes = []
    prepared = []
    for index, subset in enumerate(shard_sets):
        tasks_dir = rep_dir / f"shard{index}" / "tasks"
        copied = _copy_tasks(subset, tasks_dir)
        out = rep_dir / f"shard{index}" / "solutions.json"
        work = rep_dir / f"shard{index}" / "work"
        run_id = f"pred0006-r{rep}-s{index}"
        proc = _run_harness(
            tasks_dir, out, work, run_id, model,
            rep_dir / f"shard{index}" / "harness.log", wave2_max_tasks,
        )
        processes.append(proc)
        prepared.append((index, copied, tasks_dir, out, work, run_id))
    for proc in processes:
        proc.wait()
    rows: list[dict[str, Any]] = []
    all_correct: dict[str, bool] = {}
    for index, copied, tasks_dir, out, work, run_id in prepared:
        if not out.is_file():
            print(f"rep{rep} shard{index}: no solutions file", file=sys.stderr)
            continue
        solutions = json.loads(out.read_text(encoding="utf-8"))
        costs = _turn_costs(work / "traj" / "bash_attempts.jsonl")
        correct = _evaluate(tasks_dir, rep_dir / f"shard{index}" / "correctness.json")
        all_correct.update(correct)
        for task_id, payload in solutions.get("solutions", {}).items():
            turns = costs.get((run_id, task_id), [])
            rows.append({
                "rep": rep,
                "shard": index,
                "task_id": task_id,
                "rel": _rel_for(task_id, copied),
                "cost": int(payload.get("cost", 0)),
                "wave1_cost": turns[0] if turns else None,
                "wave2_cost": sum(turns[1:]) if len(turns) > 1 else 0,
                "turns": int(payload.get("attempts", len(turns))),
                "answered_wave1": int(
                    int(payload.get("attempts", len(turns))) == 1
                ),
                "solved_flag": bool(payload.get("solved", False)),
                "correct": bool(correct.get(task_id, False)),
                "note": payload.get("note", ""),
            })
    (rep_dir / "correctness.json").write_text(
        json.dumps(all_correct, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return rows


def _rel_for(task_id: str, copied: list[Path]) -> str:
    for path in copied:
        try:
            meta = json.loads((path / "task.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if meta.get("task_id") == task_id:
            # <category>__<label>__<number> -> category/label/number
            return "/".join(path.name.split("__"))
    return task_id


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-dir", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--examples-dir", type=Path, default=DEFAULT_EXAMPLES)
    parser.add_argument("--out-dir", type=Path,
                        default=Path(__file__).resolve().parent / "results")
    parser.add_argument("--work-dir", type=Path, default=DEFAULT_WORK)
    parser.add_argument("--reps", type=int, default=2)
    parser.add_argument("--shards", type=int, default=2)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--retry-sleep", type=float, default=10.0)
    parser.add_argument("--model", default="qwen3.6-35b-a3b-noreason")
    parser.add_argument("--wave2-max-tasks", type=int, default=0)
    parser.add_argument("--skip-examples", action="store_true")
    args = parser.parse_args(argv)

    started = time.time()
    task_dirs = _task_dirs(args.tasks_dir)
    print(f"tasks: {len(task_dirs)}; reps={args.reps}; shards={args.shards}")
    all_rows: list[dict[str, Any]] = []
    for rep in range(1, args.reps + 1):
        rep_started = time.time()
        pending = list(task_dirs)
        collected: dict[str, dict[str, Any]] = {}
        for attempt in range(args.max_retries + 1):
            if not pending:
                break
            # Distinct rep numbers keep work/correctness directories apart.
            run_rep = rep * 100 + attempt
            rows = _collect_rep(
                run_rep, pending, min(args.shards, len(pending)),
                args.work_dir, args.model, args.wave2_max_tasks,
            )
            for row in rows:
                collected[row["rel"]] = row
            missing = []
            for directory in pending:
                rel = _source_rel(directory)
                row = collected.get(rel)
                if row is None or row["turns"] == 0 or "error=" in row["note"]:
                    missing.append(directory)
            pending = missing
            print(f"rep {rep} attempt {attempt}: {len(rows)} results, "
                  f"{len(pending)} missing, {time.time() - rep_started:.0f}s")
            if pending and attempt < args.max_retries:
                time.sleep(args.retry_sleep)
        if pending:
            print(f"rep {rep}: still missing {len(pending)} tasks", file=sys.stderr)
        all_rows.extend(collected.values())
    _write_csv(all_rows, args.out_dir / "current_runs.csv")

    example_rows: list[dict[str, Any]] = []
    if not args.skip_examples:
        example_dirs = sorted(p.parent for p in args.examples_dir.glob("*/task.json"))
        for rep in range(1, args.reps + 1):
            pending = list(example_dirs)
            collected: dict[str, dict[str, Any]] = {}
            for attempt in range(args.max_retries + 1):
                if not pending:
                    break
                run_rep = rep * 100 + attempt
                rows = _collect_rep(
                    run_rep, pending, min(args.shards, len(pending)),
                    args.work_dir / "examples", args.model, args.wave2_max_tasks,
                )
                for row in rows:
                    collected[row["rel"]] = row
                missing = []
                for directory in pending:
                    rel = _source_rel(directory)
                    row = collected.get(rel)
                    if row is None or row["turns"] == 0 or "error=" in row["note"]:
                        missing.append(directory)
                pending = missing
                if pending and attempt < args.max_retries:
                    time.sleep(args.retry_sleep)
            example_rows.extend(collected.values())
        _write_csv(example_rows, args.out_dir / "example_runs.csv")

    meta = {
        "model": args.model,
        "reps": args.reps,
        "shards": args.shards,
        "wave2_max_tasks": args.wave2_max_tasks,
        "tasks": len(task_dirs),
        "current_rows": len(all_rows),
        "example_rows": len(example_rows),
        "elapsed_seconds": round(time.time() - started, 1),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "collection.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
