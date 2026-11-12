#!/usr/bin/env python3
"""Summarise lexical-marker frequencies and their raw associations.

This is a descriptive companion to ``train_predictors.py``.  It answers the
first part of the keyword hypothesis: do the phrases suggested for the
experiment occur at all in the model's first-wave reasoning, and are they
associated with the targets before any model is fitted?

Usage::

    python research/experiments/0002-first-wave-predictors/keyword_stats.py \
        --dataset .../results/horizontal/dataset.csv \
        --out .../results
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def target_values(rows: list[dict[str, str]], target: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        raw = row.get(target)
        if raw is None or str(raw).strip() == "":
            values.append(float("nan"))
        else:
            try:
                values.append(float(raw))
            except ValueError:
                values.append(float("nan"))
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    with args.dataset.open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    marker_names = []
    for key in rows[0] if rows else []:
        if key.startswith("kw_") and key.endswith("_present"):
            marker_names.append(key[len("kw_") : -len("_present")])
    marker_names.sort()

    targets = ["solvable", "solved_correctly", "remaining_tokens", "wave2_success"]
    target_data = {target: target_values(rows, target) for target in targets}

    stats = []
    for name in marker_names:
        present_key = f"kw_{name}_present"
        per100_key = f"kw_{name}_per100"
        present = [float(row.get(present_key) or 0) for row in rows]
        per100 = [float(row.get(per100_key) or 0) for row in rows]
        entry = {
            "marker": name,
            "n_present": int(sum(value > 0 for value in present)),
            "share": float(sum(value > 0 for value in present) / max(1, len(rows))),
            "mean_per100": float(sum(per100) / max(1, len(per100))),
            "max_per100": float(max(per100, default=0)),
            "correlations": {},
        }
        for target in targets:
            ys = target_data[target]
            pairs = [
                (x, y)
                for x, y in zip(per100, ys)
                if not math.isnan(y)
            ]
            entry["correlations"][target] = (
                None
                if not pairs
                else pearson([x for x, _ in pairs], [y for _, y in pairs])
            )
        stats.append(entry)

    stats.sort(key=lambda item: (-item["n_present"], item["marker"]))
    lines = ["# Лексические маркеры в первой волне", ""]
    lines.append(
        f"Наблюдений: {len(rows)}. Частота — доля задач, где маркер встретился "
        "хотя бы раз в `reasoning + content`."
    )
    lines.append("")
    lines.append("| Маркер | Есть, задач | Доля | На 100 слов (среднее) | r(solvable) | r(solved) | r(remaining) | r(w2_success) |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for item in stats:
        corr = item["correlations"]
        def fmt(value):
            return "—" if value is None else f"{value:+.3f}"
        lines.append(
            f"| {item['marker']} | {item['n_present']} | {item['share']:.3f} | "
            f"{item['mean_per100']:.3f} | {fmt(corr['solvable'])} | "
            f"{fmt(corr['solved_correctly'])} | {fmt(corr['remaining_tokens'])} | "
            f"{fmt(corr['wave2_success'])} |"
        )
    lines.append("")

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "keyword_stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    (args.out / "keyword_stats.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.out / 'keyword_stats.md'}")
    print(f"wrote {args.out / 'keyword_stats.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
