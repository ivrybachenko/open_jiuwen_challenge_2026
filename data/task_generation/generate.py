"""Regenerate the 136 solvable tasks added in the 200-task expansion.

Run from this directory::

    python3 generate.py

The script rewrites ``data/task/<category>/solvable/0007``..``0040`` and then
updates ``data/task_set/train.yaml`` and ``data/task_set/new_tasks.yaml``.  It
does not touch the organizer examples, the impossible tasks, or any report.
"""

from __future__ import annotations

import json
import random

from common import GENERATED_INDICES, TASKS_ROOT
import coding
import data_analysis_tasks
import math_tasks
import search_tasks

CATEGORIES = ["coding", "data_analysis", "math", "search"]
EXAMPLE_INDICES = {"0001", "0002"}


def _task_paths(category: str) -> list[str]:
    paths = []
    for split in ("solvable", "impossible"):
        for path in sorted((TASKS_ROOT / category / split).iterdir()):
            if path.is_dir() and (path / "task.json").is_file():
                paths.append(f"{category}/{split}/{path.name}")
    return paths


def _write_set(path, tasks: list[str]) -> None:
    lines = ["dataset:", "  random_seed: 42", "  tasks:"]
    lines += [f"    - {task}" for task in tasks]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def randomize_rewards() -> None:
    """Assign rewards independently of task type and difficulty."""
    paths = [
        TASKS_ROOT / category / "solvable" / f"{index:04d}" / "task.json"
        for category in CATEGORIES
        for index in GENERATED_INDICES
    ]
    rewards = [reward for _ in range(len(paths) // 8) for reward in range(1, 9)]
    rewards += list(range(1, len(paths) - len(rewards) + 1))
    random.Random(42).shuffle(rewards)
    for path, reward in zip(paths, rewards):
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["reward"] = reward
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def update_task_sets() -> None:
    all_tasks: list[str] = []
    new_tasks: list[str] = []
    for category in CATEGORIES:
        paths = _task_paths(category)
        all_tasks.extend(paths)
        examples = {f"{category}/solvable/{index}" for index in EXAMPLE_INDICES}
        new_tasks.extend(path for path in paths if path not in examples)
    set_dir = TASKS_ROOT.parent / "task_set"
    _write_set(set_dir / "train.yaml", all_tasks)
    _write_set(set_dir / "new_tasks.yaml", new_tasks)


def main() -> None:
    coding.generate()
    data_analysis_tasks.generate()
    math_tasks.generate()
    search_tasks.generate()
    randomize_rewards()
    update_task_sets()
    print("generated 136 solvable tasks and updated train/new_tasks sets")


if __name__ == "__main__":
    main()
