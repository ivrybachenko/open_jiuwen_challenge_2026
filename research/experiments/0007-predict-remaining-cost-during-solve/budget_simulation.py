#!/usr/bin/env python3
"""Offline budgeted wave-2 selection with the online predictor.

Reads ``policy_tasks.csv`` (one row per run/task after wave 1, with out-of-fold
``prob_correct`` and ``pred_remaining``) and simulates spending a fixed token
budget on wave 2.

Policies:

* ``model``  -- sort by predicted expected gain per predicted token;
* ``always`` -- run wave 2 in task order until the budget is exhausted;
* ``oracle`` -- sort by actual gain per actual token (upper bound);
* ``never``  -- spend nothing.

The actual score and cost of a selected wave-2 attempt come from the logged
run, so the simulation is counterfactual but uses real outcomes.

Usage::

    harness/.venv/bin/python \
        research/experiments/0007-predict-remaining-cost-during-solve/budget_simulation.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def _simulate(df: pd.DataFrame, budget: float, order: np.ndarray,
              cost_col: str, gain_col: str) -> dict[str, float]:
    spent = 0.0
    score = 0.0
    runs = 0
    for index in order:
        row = df.iloc[index]
        cost = float(row[cost_col])
        if cost <= 0:
            continue
        if spent + cost > budget:
            continue
        spent += cost
        score += float(row[gain_col])
        runs += 1
    return {
        "budget": budget,
        "runs": runs,
        "score": score,
        "cost": spent,
        "score_per_1k": 1000.0 * score / max(1.0, spent),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path,
                        default=Path(__file__).resolve().parent / "results" / "policy_tasks.csv")
    parser.add_argument("--out", type=Path,
                        default=Path(__file__).resolve().parent / "results" / "budget_report.json")
    args = parser.parse_args(argv)

    df = pd.read_csv(args.policy)
    # Only tasks that did not answer in wave 1 need a decision.
    df = df[df["answered"] == 0].reset_index(drop=True).copy()
    df["actual_gain"] = df["reward"] * df["correct"]
    df["expected_gain"] = df["reward"] * df["prob_correct"]
    df["pred_remaining"] = df["pred_remaining"].clip(lower=1.0)
    df["actual_remaining"] = df["remaining_cost"].clip(lower=0.0)
    print(f"candidate attempts: {len(df)}; tasks: {df.task_id.nunique()}")

    total_actual = float(df["actual_remaining"].sum())
    budgets = [0.1, 0.25, 0.5, 0.75, 1.0]
    df["promise_proxy"] = df["reward"] / (df["cost"] + 4000.0)
    orders = {
        "model": np.argsort(
            -(df["expected_gain"] / df["pred_remaining"]).to_numpy()),
        "promise": np.argsort(-df["promise_proxy"].to_numpy()),
        "always": np.arange(len(df)),
        "oracle": np.argsort(
            -(df["actual_gain"] / df["actual_remaining"].clip(lower=1.0)).to_numpy()),
        "cheapest": np.argsort(df["pred_remaining"].to_numpy()),
    }
    report: dict[str, object] = {"candidates": len(df),
                                 "total_actual_remaining": total_actual,
                                 "policies": {}}
    for fraction in budgets:
        budget = total_actual * fraction
        print(f"\nbudget {fraction:.0%} = {budget:.0f} tokens")
        report["policies"][f"{fraction:.2f}"] = {}
        for name, order in orders.items():
            row = _simulate(df, budget, order, "actual_remaining", "actual_gain")
            report["policies"][f"{fraction:.2f}"][name] = row
            print(f"  {name:9s} runs={row['runs']:3d} score={row['score']:6.1f} "
                  f"cost={row['cost']:8.0f} score/1k={row['score_per_1k']:.3f}")
        never = {"budget": budget, "runs": 0, "score": 0.0, "cost": 0.0,
                 "score_per_1k": 0.0}
        report["policies"][f"{fraction:.2f}"]["never"] = never

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
