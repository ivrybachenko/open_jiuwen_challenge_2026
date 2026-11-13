#!/usr/bin/env python3
"""Evaluate the LLM cost probe against actual costs and the static model.

Usage::

    harness/.venv/bin/python \
        research/experiments/0009-llm-cost-probe/evaluate_probe.py \
        --probe research/experiments/0009-llm-cost-probe/results/probe_raw.jsonl \
        --runs research/experiments/0006-predict-cost-before-solve/results/current_runs.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import mean_absolute_error, roc_auc_score


def _spearman(a, b) -> float:
    value = spearmanr(a, b).correlation
    return 0.0 if value is None or not np.isfinite(value) else float(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--static", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    probe = pd.read_json(args.probe, lines=True)
    probe = probe[probe["parsed"].notna()].copy()
    probe["tokens"] = probe["parsed"].map(
        lambda value: value.get("tokens") if isinstance(value, dict) else None)
    probe["solvable"] = probe["parsed"].map(
        lambda value: value.get("solvable") if isinstance(value, dict) else None)
    probe["bucket"] = probe["parsed"].map(
        lambda value: value.get("bucket") if isinstance(value, dict) else None)
    probe["needs_second_turn"] = probe["parsed"].map(
        lambda value: value.get("needs_second_turn")
        if isinstance(value, dict) else None)
    probe = probe.dropna(subset=["tokens"])

    runs = pd.read_csv(args.runs)
    agg = runs.groupby("rel").agg(
        cost=("cost", "mean"),
        correct=("correct", "mean"),
        impossible=("rel", lambda values: int("impossible" in values.iloc[0])),
    )
    df = probe.merge(agg, left_on="rel", right_index=True, how="inner")
    print(f"matched: {len(df)}")
    y = df["cost"].astype(float).values
    pred = df["tokens"].astype(float).values
    report: dict[str, object] = {
        "n": int(len(df)),
        "mae": float(mean_absolute_error(y, pred)),
        "spearman": _spearman(y, pred),
        "median_actual": float(np.median(y)),
        "median_probe": float(np.median(pred)),
        "probe_input_tokens": int(df["input_tokens"].sum()),
        "probe_output_tokens": int(df["output_tokens"].sum()),
        "probe_cost_tokens": int(
            (df["output_tokens"] + np.ceil(df["input_tokens"] / 10)).sum()),
    }
    base = np.full(len(y), np.median(y))
    report["mae_median_baseline"] = float(mean_absolute_error(y, base))
    if df["solvable"].notna().any():
        mask = df["solvable"].notna()
        report["solvable_auc"] = float(roc_auc_score(
            df.loc[mask, "impossible"] == 0, df.loc[mask, "solvable"].astype(int)))
    report["bucket_counts"] = df["bucket"].value_counts().to_dict()
    report["tokens_by_bucket"] = df.groupby("bucket")["tokens"].median().to_dict()
    report["actual_by_bucket"] = df.groupby("bucket")["cost"].median().to_dict()
    if args.static and Path(args.static).is_file():
        static = pd.read_csv(args.static)
        merged = df.merge(static[["rel", "predicted"]], on="rel", how="inner")
        if len(merged) >= 5:
            report["static_spearman"] = _spearman(
                merged["cost"], merged["predicted"])
            report["static_mae"] = float(mean_absolute_error(
                merged["cost"], merged["predicted"]))
            report["n_static"] = int(len(merged))
    args.out = args.out or args.probe.with_name("probe_report.json")
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
