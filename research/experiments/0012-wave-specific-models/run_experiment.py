#!/usr/bin/env python3
"""Collect fresh multi-wave trajectories on the 32-task research set.

The stock harness is used unchanged.  ``--max-waves 6`` and
``--wave2-max-tasks 0`` make it continue every candidate that the current
model still considers promising, which produces the wave-3+ rows that the
existing research runs do not have.

Usage::

    LLM_API_KEY="$NEURAL_DEEP_API_KEY" \\
      harness/.venv/bin/python \\
      research/experiments/0012-wave-specific-models/run_experiment.py \\
      --repeats 2 --max-waves 6
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
sys.path.insert(0, str(REPO_ROOT))

from evaluation.common.paths import (  # noqa: E402
    default_tasks_root,
    resolve_task_set_path,
)
from evaluation.common.runner import (  # noqa: E402
    HarnessConfig,
    read_solutions,
    resolve_python,
    run_harness,
)
from evaluation.common.suite import (  # noqa: E402
    evaluate_suite,
    outcome_to_dict,
    prepare_suite,
    summarize,
)
from evaluation.common.tasks import (  # noqa: E402
    load_task_set,
    resolve_task_set,
)

NOREASON = "qwen3.6-35b-a3b-noreason"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tasks-yaml",
        type=Path,
        default=(
            REPO_ROOT / "research" / "experiments"
            / "0003-reasoning-models-and-explanations" / "tasks.yaml"
        ),
    )
    parser.add_argument(
        "--out-dir", type=Path, default=SCRIPT_DIR / "results"
    )
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--max-tasks", type=int, default=None)
    parser.add_argument("--budget", type=int, default=None)
    parser.add_argument("--max-waves", type=int, default=6)
    parser.add_argument("--wave2-max-tasks", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=3600.0)
    parser.add_argument("--model", default=NOREASON)
    parser.add_argument("--python", default=None)
    parser.add_argument("--tag", default="exp0012")
    parser.add_argument("--skip-existing", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not os.environ.get("LLM_API_KEY"):
        print(
            'error: set LLM_API_KEY, e.g. LLM_API_KEY="$NEURAL_DEEP_API_KEY"',
            file=sys.stderr,
        )
        return 2

    spec = load_task_set(resolve_task_set_path(args.tasks_yaml))
    tasks = resolve_task_set(spec, default_tasks_root())
    if args.max_tasks is not None:
        tasks = tasks[: args.max_tasks]
    print(f"task set {spec.name}: {len(tasks)} tasks")

    for repeat in range(1, args.repeats + 1):
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        run_id = f"{args.tag}-r{repeat}-{stamp}"
        run_dir = args.out_dir / f"run-{repeat:02d}"
        if args.skip_existing and (run_dir / "summary.json").is_file():
            print(f"skip existing {run_dir}")
            continue
        work_dir = run_dir / "work"
        traj_dir = run_dir / "traj"
        work_dir.mkdir(parents=True, exist_ok=True)
        traj_dir.mkdir(parents=True, exist_ok=True)
        prepared = prepare_suite(tasks, work_dir)
        config = HarnessConfig(
            repo_root=REPO_ROOT,
            python=args.python,
            model=args.model,
            budget=args.budget,
            run_id=run_id,
            save_trajectories=True,
            trajectories_dir=traj_dir,
            extra_args=(
                "--max-waves",
                str(args.max_waves),
                "--wave2-max-tasks",
                str(args.wave2_max_tasks),
                "--log-level",
                "WARNING",
            ),
            timeout=args.timeout,
        )
        out_path = run_dir / "solutions.json"
        print(f"[{run_id}] running {len(tasks)} tasks ...")
        run = run_harness(config, prepared.tasks_dir, out_path)
        solutions = read_solutions(out_path)
        outcomes = evaluate_suite(
            prepared,
            solutions,
            python=args.python or resolve_python(config),
            forbid_test_edits=True,
        )
        summary = summarize(outcomes)
        payload = {
            "run_id": run_id,
            "repeat": repeat,
            "model": args.model,
            "max_waves": args.max_waves,
            "command": run.command,
            "returncode": run.returncode,
            "timed_out": run.timed_out,
            "duration_seconds": run.duration_seconds,
            "summary": summary.to_dict(),
            "tasks": [outcome_to_dict(item) for item in outcomes],
            "work_dir": str(work_dir),
        }
        (run_dir / "summary.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        with (run_dir / "tasks.jsonl").open("w", encoding="utf-8") as stream:
            for item in payload["tasks"]:
                stream.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(
            f"[{run_id}] score={summary.score:g}/{summary.max_score:g} "
            f"solved={summary.solved_tasks}/{summary.total_tasks} "
            f"cost={summary.cost} time={run.duration_seconds:.0f}s"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
