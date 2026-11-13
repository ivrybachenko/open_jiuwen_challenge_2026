#!/usr/bin/env python3
"""Plots for experiments 0006 and 0007.

Usage::

    harness/.venv/bin/python \
        research/experiments/0006-predict-cost-before-solve/make_figures.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _cost_by_category(runs: Path, out: Path) -> None:
    df = pd.read_csv(runs)
    df["category"] = df["rel"].str.split("/").str[0]
    df["label"] = df["rel"].str.split("/").str[1]
    categories = ["coding", "math", "data_analysis", "search"]
    data = [df[df["category"] == c]["cost"].values for c in categories]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.boxplot(data, tick_labels=categories, showfliers=False)
    ax.set_ylabel("total tokens per attempt")
    ax.set_title("Cost by category, current harness (v0003)")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "cost_by_category.png", dpi=160)
    plt.close(fig)


def _predicted_vs_actual(path: Path, out: Path) -> None:
    if not path.is_file():
        return
    df = pd.read_csv(path)
    fig, ax = plt.subplots(figsize=(5.5, 5))
    colors = np.where(df["impossible"] == 1, "#c0392b", "#2c7fb8")
    ax.scatter(df["actual"], df["predicted"], c=colors, alpha=0.75, edgecolor="k",
               linewidth=0.3)
    upper = max(df["actual"].max(), df["predicted"].max()) * 1.05
    ax.plot([0, upper], [0, upper], "k--", linewidth=1, label="ideal")
    ax.set_xlabel("actual mean cost, tokens")
    ax.set_ylabel("out-of-fold prediction, tokens")
    ax.set_title("Pre-solve cost prediction (blue solvable, red impossible)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "predicted_vs_actual.png", dpi=160)
    plt.close(fig)


def _online_probability(path: Path, out: Path) -> None:
    if not path.is_file():
        return
    df = pd.read_csv(path)
    fig, ax = plt.subplots(figsize=(7, 4))
    for value, label, color in ((0, "incorrect", "#c0392b"),
                                (1, "correct", "#2c7fb8")):
        subset = df[df["correct"] == value]["prob_correct"]
        ax.hist(subset, bins=20, alpha=0.6, label=label, color=color,
                density=True)
    ax.set_xlabel("predicted P(correct after solving)")
    ax.set_ylabel("density")
    ax.set_title("Online success prediction after the first turn")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "online_prob_correct.png", dpi=160)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    parser.add_argument("--current-runs", type=Path,
                        default=here / "results" / "current_runs.csv")
    parser.add_argument("--predictions", type=Path,
                        default=here / "results" / "static_predictions.csv")
    parser.add_argument("--policy", type=Path,
                        default=here.parent / "0007-predict-remaining-cost-during-solve"
                        / "results" / "policy_tasks.csv")
    parser.add_argument("--out-dir", type=Path, default=here / "results")
    args = parser.parse_args(argv)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if args.current_runs.is_file():
        _cost_by_category(args.current_runs, args.out_dir)
    _predicted_vs_actual(args.predictions, args.out_dir)
    _online_probability(args.policy, args.out_dir)
    print(f"figures written to {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
