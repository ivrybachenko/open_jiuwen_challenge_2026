#!/usr/bin/env python3
"""Run experiment 0004: solve in one turn or collect data for the next turn.

Every configuration is run on a fresh copy of the 32-task set.  The stock
harness is launched through ``experiment_agent.py``; only the system prompt
differs between ``base`` and ``goal``.

Examples::

    python research/experiments/0004-solve-or-collect-next-turn-data/run_experiment.py
    python research/experiments/0004-solve-or-collect-next-turn-data/run_experiment.py \\
        --configs base-nn,goal-nn --repeats 2 --max-tasks 8
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
sys.path.insert(0, str(REPO_ROOT))

from evaluation.common.cost import token_cost  # noqa: E402
from evaluation.common.paths import default_tasks_root, repo_root  # noqa: E402
from evaluation.common.runner import read_solutions, resolve_python  # noqa: E402
from evaluation.common.suite import (  # noqa: E402
    evaluate_suite,
    outcome_to_dict,
    prepare_suite,
    summarize,
)
from evaluation.common.tasks import load_task_set, resolve_task_set  # noqa: E402

NOREASON = "qwen3.6-35b-a3b-noreason"
REASONING = "qwen3.6-35b-a3b"
DEFAULT_BASE_URL = "https://api.neuraldeep.ru/v1"


@dataclass(frozen=True)
class Config:
    name: str
    model: str
    goal: bool


CONFIGS = (
    Config("base-nn", NOREASON, False),
    Config("goal-nn", NOREASON, True),
    Config("base-r", REASONING, False),
    Config("goal-r", REASONING, True),
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tasks-yaml",
        type=Path,
        default=SCRIPT_DIR / "tasks.yaml",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=SCRIPT_DIR / "results",
    )
    parser.add_argument(
        "--configs",
        default=",".join(config.name for config in CONFIGS),
    )
    parser.add_argument("--repeats", type=int, default=4)
    parser.add_argument("--max-tasks", type=int, default=None)
    parser.add_argument("--timeout", type=float, default=7200.0)
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Keep a run directory that already has summary.json.",
    )
    parser.add_argument("--keep-work", action="store_true")
    parser.add_argument("--python", default=None, help="Harness interpreter.")
    parser.add_argument("--log-level", default="WARNING")
    return parser.parse_args(argv)


def _check_env() -> None:
    if not os.environ.get("LLM_API_KEY"):
        raise SystemExit(
            'error: set LLM_API_KEY, e.g. LLM_API_KEY="$NEURAL_DEEP_API_KEY"'
        )


def _parse_configs(raw: str) -> list[Config]:
    by_name = {config.name: config for config in CONFIGS}
    names = [name.strip() for name in raw.split(",") if name.strip()]
    unknown = [name for name in names if name not in by_name]
    if unknown:
        raise SystemExit(
            f"error: unknown config(s) {', '.join(unknown)}; "
            f"available: {', '.join(by_name)}"
        )
    return [by_name[name] for name in names]


def _read_attempts(path: Path) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return grouped
    for line in lines:
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        grouped.setdefault(str(record.get("task_id")), []).append(record)
    return grouped


_COMMAND_RE = re.compile(
    r"\b(cat|head|tail|grep|find|ls|awk|sed|cut|sort|uniq|wc|python3?|pytest|unittest)\b"
)


def _script_stats(record: dict[str, Any]) -> dict[str, Any]:
    script = str(record.get("script") or "")
    features = record.get("features") or {}
    commands = [
        line.strip()
        for line in script.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    return {
        "script_chars": len(script),
        "script_lines": len(commands),
        "has_cat": bool(re.search(r"\bcat\b", script)),
        "has_head_tail": bool(re.search(r"\b(head|tail)\b", script)),
        "has_grep": bool(re.search(r"\bgrep\b", script)),
        "has_find": bool(re.search(r"\bfind\b", script)),
        "has_python": bool(re.search(r"\bpython3?\b", script)),
        "has_tests": bool(re.search(r"\b(pytest|unittest|test_[A-Za-z0-9_]+\.py)\b", script)),
        "has_write_answer": bool(re.search(r"answer\.txt", script)),
        "mentions": [m.group(0) for m in _COMMAND_RE.finditer(script)],
        "output_chars": int(features.get("output_chars") or 0),
        "exit_code": features.get("exit_code"),
        "hit_token_limit": bool(features.get("hit_token_limit")),
    }


def _record_stats(record: dict[str, Any]) -> dict[str, Any]:
    input_tokens = int(record.get("input_tokens") or 0)
    output_tokens = int(record.get("output_tokens") or 0)
    features = record.get("features") or {}
    return {
        "model": record.get("model"),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": token_cost(input_tokens, output_tokens),
        "answer_kind": record.get("answer_kind") or "none",
        "answer_present": bool(record.get("answer")),
        "hit_token_limit": bool(features.get("hit_token_limit")),
        "finish_reason": record.get("finish_reason") or "",
        "duration_seconds": float(record.get("duration_seconds") or 0.0),
        **_script_stats(record),
    }


def _wave_summary(attempts: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    wave1 = [
        _record_stats(rec)
        for recs in attempts.values()
        for rec in recs
        if rec.get("wave") == 1
    ]
    wave2 = [
        _record_stats(rec)
        for recs in attempts.values()
        for rec in recs
        if rec.get("wave") == 2
    ]

    def block(records: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "turns": len(records),
            "input_tokens": sum(item["input_tokens"] for item in records),
            "output_tokens": sum(item["output_tokens"] for item in records),
            "cost": sum(item["cost"] for item in records),
            "answered": sum(
                1 for item in records if item["answer_kind"] in {"done", "value"}
            ),
            "impossible": sum(
                1 for item in records if item["answer_kind"] == "impossible"
            ),
            "hit_token_limit": sum(
                1 for item in records if item["hit_token_limit"]
            ),
            "script_chars": sum(item["script_chars"] for item in records),
            "script_lines": sum(item["script_lines"] for item in records),
            "output_chars": sum(item["output_chars"] for item in records),
        }

    wave1_summary = block(wave1)
    wave2_summary = block(wave2)
    wave1_summary["answered_tasks"] = len(
        {
            task_id
            for task_id, recs in attempts.items()
            if any(
                rec.get("wave") == 1
                and rec.get("answer_kind") in {"done", "value"}
                for rec in recs
            )
        }
    )
    wave2_summary["tasks"] = len(
        {
            task_id
            for task_id, recs in attempts.items()
            if any(rec.get("wave") == 2 for rec in recs)
        }
    )
    return {"wave1": wave1_summary, "wave2": wave2_summary}


def _task_rows(
    outcomes,
    config: Config,
    attempts: dict[str, list[dict[str, Any]]],
    repeat: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for outcome in outcomes:
        task_id = outcome.task.task_id
        recs = attempts.get(task_id, [])
        waves = {
            int(rec.get("wave") or 0): _record_stats(rec)
            for rec in recs
            if rec.get("wave") in (1, 2)
        }
        base = outcome_to_dict(outcome)
        wave1 = waves.get(1)
        wave2 = waves.get(2)
        wave1_answered = bool(
            wave1 and wave1["answer_kind"] in {"done", "value"}
        )
        base.update(
            {
                "wave1": wave1,
                "wave2": wave2,
                "wave1_answered": wave1_answered,
                "wave1_unanswered": not wave1_answered,
                "wave1_closed": bool(wave1_answered and outcome.verdict.solved),
                "wave2_solved": bool(
                    not wave1_answered and wave2 is not None and outcome.verdict.solved
                ),
                "config": config.name,
                "repeat": repeat,
            }
        )
        rows.append(base)
    return rows


def _run_config(
    config: Config,
    tasks,
    args: argparse.Namespace,
    harness_python: str,
    repeat: int,
    config_dir: Path,
) -> dict[str, Any]:
    summary_path = config_dir / "summary.json"
    if args.skip_existing and summary_path.is_file():
        print(f"[skip] {config.name} r{repeat}: {summary_path} exists")
        return json.loads(summary_path.read_text(encoding="utf-8"))

    if config_dir.exists():
        shutil.rmtree(config_dir)
    config_dir.mkdir(parents=True, exist_ok=True)

    prepared = prepare_suite(tasks, config_dir / "work")
    out_path = config_dir / "solutions.json"
    trajectories = config_dir / "traj"
    agents = config_dir / "agents"
    run_id = (
        f"exp0004-{config.name}-r{repeat}-"
        f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    )

    command = [
        harness_python,
        str(SCRIPT_DIR / "experiment_agent.py"),
        "--tasks-dir",
        str(prepared.tasks_dir),
        "--out",
        str(out_path),
        "--agent-workspace",
        str(agents),
        "--trajectories-dir",
        str(trajectories),
        "--run-id",
        run_id,
        "--model",
        config.model,
        "--wave1-max-tokens",
        "1000",
        "--wave2-max-tokens",
        "4000",
        "--wave2-max-tasks",
        "50",
        "--log-level",
        args.log_level.upper(),
    ]
    env = os.environ.copy()
    env.setdefault("LLM_BASE_URL", DEFAULT_BASE_URL)
    env["EXP_GOAL_PROMPT"] = "1" if config.goal else "0"
    env["PYTHONPATH"] = os.pathsep.join(
        part
        for part in (str(REPO_ROOT / "harness" / "src"), env.get("PYTHONPATH", ""))
        if part
    )
    env.setdefault("PYTHONUNBUFFERED", "1")

    print(
        f"[run] {config.name} r{repeat}: model={config.model} "
        f"goal={int(config.goal)} tasks={len(prepared.tasks)}"
    )
    started = time.monotonic()
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=args.timeout,
        )
        returncode = completed.returncode
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = 124
        stdout = (
            (exc.stdout or b"").decode("utf-8", "replace")
            if isinstance(exc.stdout, bytes)
            else (exc.stdout or "")
        )
        stderr = (
            (exc.stderr or b"").decode("utf-8", "replace")
            if isinstance(exc.stderr, bytes)
            else (exc.stderr or "")
        )
    duration = time.monotonic() - started

    (config_dir / "harness.log").write_text(
        "COMMAND: "
        + " ".join(command)
        + "\n\nSTDOUT\n"
        + stdout
        + "\n\nSTDERR\n"
        + stderr,
        encoding="utf-8",
    )
    solutions = read_solutions(out_path)
    outcomes = evaluate_suite(
        prepared,
        solutions,
        python=harness_python,
        forbid_test_edits=True,
    )
    summary = summarize(outcomes)
    attempts = _read_attempts(trajectories / "bash_attempts.jsonl")
    waves = _wave_summary(attempts)
    rows = _task_rows(outcomes, config, attempts, repeat)

    payload = {
        "config": {
            "name": config.name,
            "model": config.model,
            "goal": config.goal,
        },
        "run_id": run_id,
        "repeat": repeat,
        "command": command,
        "returncode": returncode,
        "timed_out": timed_out,
        "duration_seconds": round(duration, 3),
        "summary": summary.to_dict(),
        "waves": waves,
        "task_set": str(args.tasks_yaml),
        "tasks": rows,
    }
    summary_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (config_dir / "tasks.jsonl").open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")

    if not args.keep_work:
        shutil.rmtree(config_dir / "work", ignore_errors=True)

    print(
        f"[done] {config.name} r{repeat}: "
        f"score={summary.score:g}/{summary.max_score:g} "
        f"solved={summary.solved_tasks}/{summary.total_tasks} "
        f"cost={summary.cost} wave1={waves['wave1']['cost']} "
        f"wave1_answered={waves['wave1']['answered_tasks']} "
        f"wave2={waves['wave2']['cost']} "
        f"rc={returncode} t={duration:.1f}s"
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    _check_env()
    if args.max_tasks is not None:
        args.max_tasks = max(1, args.max_tasks)
    if args.repeats < 1:
        raise SystemExit("error: --repeats must be >= 1")
    args.out_dir = args.out_dir.resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    spec = load_task_set(args.tasks_yaml)
    tasks = resolve_task_set(spec, default_tasks_root())
    if args.max_tasks is not None:
        tasks = tasks[: args.max_tasks]

    harness_python = args.python or resolve_python(
        type("Cfg", (), {"repo_root": repo_root(), "python": None})()
    )
    configs = _parse_configs(args.configs)

    print(
        f"experiment 0004: {len(tasks)} tasks, {len(configs)} configs, "
        f"{args.repeats} repeat(s), python={harness_python}"
    )
    payloads = []
    for repeat in range(1, args.repeats + 1):
        for config in configs:
            config_dir = args.out_dir / config.name / f"run-{repeat:02d}"
            payload = _run_config(
                config, tasks, args, harness_python, repeat, config_dir
            )
            payloads.append(payload)

    print("\nsummary")
    print(
        f"{'config':<10} {'run':>3} {'score':>7} {'solved':>7} {'cost':>8} "
        f"{'w1 cost':>8} {'w1 ans':>7} {'w2 cost':>8}"
    )
    for payload in payloads:
        waves = payload["waves"]
        summary = payload["summary"]
        print(
            f"{payload['config']['name']:<10} {payload['repeat']:>3} "
            f"{summary['score']:>7g} "
            f"{summary['solved_tasks']:>3}/{summary['total_tasks']:<3} "
            f"{summary['cost']:>8} {waves['wave1']['cost']:>8} "
            f"{waves['wave1']['answered_tasks']:>7} {waves['wave2']['cost']:>8}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
