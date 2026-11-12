#!/usr/bin/env python3
"""Compare horizontal and vertical train/validation/test splits.

Reads one or more ``results.json`` files produced by ``train_predictors.py``
and writes a Markdown + JSON comparison.  The comparison is intentionally
built around the questions from the experiment:

* does a model trained on all categories (horizontal split) transfer to new
  tasks of the same categories?
* does a model trained on two categories transfer to a completely unseen
  category (vertical split)?
* do lexical markers in the reasoning improve both?
* how much does the static instruction/workspace feature set add, and is that
  gain stable across splits?

Usage::

    python research/experiments/0002-first-wave-predictors/compare_splits.py \
        --run horizontal=.../results/horizontal \
        --run vertical-search=.../results/vertical-search \
        --run vertical-math=.../results/vertical-math \
        --out .../results
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

FEATURE_ORDER = ["turn", "turn_overview", "turn_keywords", "full"]
CLASSIFICATION_TARGETS = [
    "solvable",
    "solved_correctly",
    "wave2_any_answer",
    "wave2_success",
]
REGRESSION_TARGETS = ["remaining_tokens", "remaining_turns", "wave2_cost"]


def load_run(label: str, path: Path) -> dict[str, Any]:
    results_path = path / "results.json" if path.is_dir() else path
    payload = json.loads(results_path.read_text(encoding="utf-8"))
    return {"label": label, "path": str(path), "results": payload}


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "—"
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return "—"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def get_metric(entry: dict[str, Any] | None, split: str, metric: str) -> Any:
    if not entry:
        return None
    best = entry.get("best")
    if not best:
        return None
    if split == "val":
        if metric in best:
            return best.get(metric)
        return (best.get("val") or {}).get(metric)
    return (best.get("test") or {}).get(metric)


def get_model(entry: dict[str, Any] | None) -> str:
    if not entry:
        return "—"
    best = entry.get("best")
    if not best:
        return "—"
    return str(best.get("model_name") or "—")


def table_for_metric(
    runs: list[dict[str, Any]],
    target: str,
    *,
    task: str,
    metric: str,
    split: str = "test",
) -> list[str]:
    lines = [f"| Набор признаков | {' | '.join(run['label'] for run in runs)} |"]
    lines.append("| --- | " + " | ".join("---:" for _ in runs) + " |")
    for feature_set in FEATURE_ORDER:
        row = [f"| {feature_set}"]
        for run in runs:
            entry = (run["results"].get("primary", {}).get(target) or {}).get(feature_set)
            row.append(fmt(get_metric(entry, split, metric)))
        lines.append(" | ".join(row) + " |")
    return lines


def table_models(runs: list[dict[str, Any]], target: str) -> list[str]:
    lines = [f"| Набор признаков | {' | '.join(run['label'] for run in runs)} |"]
    lines.append("| --- | " + " | ".join("---" for _ in runs) + " |")
    for feature_set in FEATURE_ORDER:
        row = [f"| {feature_set}"]
        for run in runs:
            entry = (run["results"].get("primary", {}).get(target) or {}).get(feature_set)
            row.append(get_model(entry))
        lines.append(" | ".join(row) + " |")
    return lines


def delta(
    run: dict[str, Any],
    target: str,
    left: str,
    right: str,
    *,
    task: str,
    metric: str,
) -> float | None:
    entries = run["results"].get("primary", {}).get(target) or {}
    left_value = get_metric(entries.get(left), "test", metric)
    right_value = get_metric(entries.get(right), "test", metric)
    if left_value is None or right_value is None:
        return None
    try:
        return float(left_value) - float(right_value)
    except (TypeError, ValueError):
        return None


def external_table(
    runs: list[dict[str, Any]],
    target: str,
    *,
    task: str,
    metric: str,
) -> list[str]:
    lines = [f"| Набор признаков | {' | '.join(run['label'] for run in runs)} |"]
    lines.append("| --- | " + " | ".join("---:" for _ in runs) + " |")
    for feature_set in FEATURE_ORDER:
        row = [f"| {feature_set}"]
        for run in runs:
            entry = (
                run["results"].get("external", {}).get(target) or {}
            ).get(feature_set) or {}
            subset = entry.get("all") or {}
            row.append(fmt((subset.get("metrics") or {}).get(metric)))
        lines.append(" | ".join(row) + " |")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run",
        action="append",
        required=True,
        help="label=path to a results directory or results.json",
    )
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument(
        "--horizontal-label",
        default="horizontal",
        help="Run label that is the horizontal baseline.",
    )
    args = parser.parse_args(argv)

    runs: list[dict[str, Any]] = []
    for item in args.run:
        label, _, path = item.partition("=")
        if not path:
            raise SystemExit(f"--run must be label=path, got {item!r}")
        runs.append(load_run(label, Path(path)))
    args.out.mkdir(parents=True, exist_ok=True)

    lines: list[str] = ["# Сравнение горизонтального и вертикального разбиений", ""]
    lines.append("## Состав разбиений")
    lines.append("")
    lines.append("| Прогон | Режим | Задачи train/val/test | Типы |")
    lines.append("| --- | --- | --- | --- |")
    for run in runs:
        split = run["results"].get("split", {})
        tasks = split.get("tasks", {})
        if split.get("mode") == "horizontal":
            types_text = "все категории"
        else:
            types_text = (
                f"{split.get('vertical_train_types') or '—'} → "
                f"{split.get('vertical_val_type') or '—'} / "
                f"{split.get('vertical_test_type') or '—'}"
            )
        lines.append(
            f"| {run['label']} | {split.get('mode', '?')} | "
            f"{tasks.get('train', '?')}/{tasks.get('val', '?')}/{tasks.get('test', '?')} | "
            f"{types_text} |"
        )
    lines.append("")

    for target in CLASSIFICATION_TARGETS:
        if not any(target in run["results"].get("primary", {}) for run in runs):
            continue
        lines.append(f"## {target}")
        lines.append("")
        lines.append("ROC-AUC на test:")
        lines.append("")
        lines.extend(table_for_metric(runs, target, task="classification", metric="roc_auc"))
        lines.append("")
        lines.append("PR-AUC на test:")
        lines.append("")
        lines.extend(
            table_for_metric(runs, target, task="classification", metric="average_precision")
        )
        lines.append("")
        lines.append("Brier на test:")
        lines.append("")
        lines.extend(table_for_metric(runs, target, task="classification", metric="brier"))
        lines.append("")
        lines.append("Выбранные модели:")
        lines.append("")
        lines.extend(table_models(runs, target))
        lines.append("")

    for target in REGRESSION_TARGETS:
        if not any(target in run["results"].get("primary", {}) for run in runs):
            continue
        lines.append(f"## {target}")
        lines.append("")
        lines.append("MAE на test:")
        lines.append("")
        lines.extend(table_for_metric(runs, target, task="regression", metric="mae"))
        lines.append("")
        lines.append("Spearman на test:")
        lines.append("")
        lines.extend(
            table_for_metric(runs, target, task="regression", metric="spearman")
        )
        lines.append("")
        lines.append("R² на test:")
        lines.append("")
        lines.extend(table_for_metric(runs, target, task="regression", metric="r2"))
        lines.append("")
        lines.append("Выбранные модели:")
        lines.append("")
        lines.extend(table_models(runs, target))
        lines.append("")

    horizontal_runs = [run for run in runs if run["label"] == args.horizontal_label]
    vertical_runs = [run for run in runs if run["label"].startswith("vertical")]
    if horizontal_runs and vertical_runs:
        lines.append("## Сводка: горизонтальное vs вертикальные разбиения")
        lines.append("")
        lines.append(
            "Для вертикальных разбиений показаны среднее и диапазон по ротациям. "
            "Δ — среднее вертикальное минус горизонтальное; для ROC-AUC "
            "положительная Δ означает лучше, для MAE — хуже."
        )
        lines.append("")
        for target in CLASSIFICATION_TARGETS:
            if not any(target in run["results"].get("primary", {}) for run in runs):
                continue
            lines.append(f"### {target}, ROC-AUC")
            lines.append("")
            lines.append("| Набор признаков | Горизонт. | Вертик. среднее | Вертик. диапазон | Δ |")
            lines.append("| --- | ---: | ---: | --- | ---: |")
            for feature_set in FEATURE_ORDER:
                values = []
                for run in vertical_runs:
                    entry = (run["results"].get("primary", {}).get(target) or {}).get(feature_set)
                    value = get_metric(entry, "test", "roc_auc")
                    if value is not None:
                        values.append(float(value))
                horiz_entry = (
                    horizontal_runs[0]["results"].get("primary", {}).get(target) or {}
                ).get(feature_set)
                horiz_value = get_metric(horiz_entry, "test", "roc_auc")
                if not values:
                    continue
                mean = sum(values) / len(values)
                lines.append(
                    f"| {feature_set} | {fmt(horiz_value)} | {fmt(mean)} | "
                    f"{fmt(min(values))}–{fmt(max(values))} | "
                    f"{fmt(mean - float(horiz_value)) if horiz_value is not None else '—'} |"
                )
            lines.append("")
        for target in REGRESSION_TARGETS:
            if not any(target in run["results"].get("primary", {}) for run in runs):
                continue
            lines.append(f"### {target}, MAE (меньше лучше)")
            lines.append("")
            lines.append("| Набор признаков | Горизонт. | Вертик. среднее | Вертик. диапазон | Δ |")
            lines.append("| --- | ---: | ---: | --- | ---: |")
            for feature_set in FEATURE_ORDER:
                values = []
                for run in vertical_runs:
                    entry = (run["results"].get("primary", {}).get(target) or {}).get(feature_set)
                    value = get_metric(entry, "test", "mae")
                    if value is not None:
                        values.append(float(value))
                horiz_entry = (
                    horizontal_runs[0]["results"].get("primary", {}).get(target) or {}
                ).get(feature_set)
                horiz_value = get_metric(horiz_entry, "test", "mae")
                if not values:
                    continue
                mean = sum(values) / len(values)
                lines.append(
                    f"| {feature_set} | {fmt(horiz_value)} | {fmt(mean)} | "
                    f"{fmt(min(values))}–{fmt(max(values))} | "
                    f"{fmt(mean - float(horiz_value)) if horiz_value is not None else '—'} |"
                )
            lines.append("")

    lines.append("## Гипотеза о ключевых словах")
    lines.append("")
    lines.append(
        "Разница `turn_keywords - turn` на test. Для классификации — ROC-AUC "
        "(больше лучше), для регрессии — MAE (меньше лучше)."
    )
    lines.append("")
    lines.append(f"| Цель | Метрика | {' | '.join(run['label'] for run in runs)} |")
    lines.append("| --- | --- | " + " | ".join("---:" for _ in runs) + " |")
    for target in CLASSIFICATION_TARGETS:
        if not any(target in run["results"].get("primary", {}) for run in runs):
            continue
        row = [f"| {target} | Δ ROC-AUC"]
        for run in runs:
            row.append(fmt(delta(run, target, "turn_keywords", "turn", task="classification", metric="roc_auc")))
        lines.append(" | ".join(row) + " |")
    for target in REGRESSION_TARGETS:
        if not any(target in run["results"].get("primary", {}) for run in runs):
            continue
        row = [f"| {target} | Δ MAE"]
        for run in runs:
            row.append(fmt(delta(run, target, "turn_keywords", "turn", task="regression", metric="mae")))
        lines.append(" | ".join(row) + " |")
    lines.append("")

    lines.append("## Статические признаки и переобучение")
    lines.append("")
    lines.append(
        "Разница `full - turn_overview` на test. Если она положительна, "
        "статические признаки задачи помогают; если исчезает на вертикальном "
        "разбиении — модель опирается на особенности категорий/генератора."
    )
    lines.append("")
    lines.append(f"| Цель | Метрика | {' | '.join(run['label'] for run in runs)} |")
    lines.append("| --- | --- | " + " | ".join("---:" for _ in runs) + " |")
    for target in CLASSIFICATION_TARGETS:
        if not any(target in run["results"].get("primary", {}) for run in runs):
            continue
        row = [f"| {target} | Δ ROC-AUC"]
        for run in runs:
            row.append(fmt(delta(run, target, "full", "turn_overview", task="classification", metric="roc_auc")))
        lines.append(" | ".join(row) + " |")
    for target in REGRESSION_TARGETS:
        if not any(target in run["results"].get("primary", {}) for run in runs):
            continue
        row = [f"| {target} | Δ MAE"]
        for run in runs:
            row.append(fmt(delta(run, target, "full", "turn_overview", task="regression", metric="mae")))
        lines.append(" | ".join(row) + " |")
    lines.append("")

    has_external = any(run["results"].get("external") for run in runs)
    if has_external:
        lines.append("## Внешняя проверка на других прогонах")
        lines.append("")
        for target in CLASSIFICATION_TARGETS:
            if target not in {"solvable", "wave2_any_answer", "wave2_success"}:
                continue
            lines.append(f"### {target}, ROC-AUC")
            lines.append("")
            lines.extend(
                external_table(runs, target, task="classification", metric="roc_auc")
            )
            lines.append("")
        for target in REGRESSION_TARGETS:
            lines.append(f"### {target}, MAE")
            lines.append("")
            lines.extend(external_table(runs, target, task="regression", metric="mae"))
            lines.append("")

    # Machine-readable comparison.
    comparison: dict[str, Any] = {"runs": []}
    for run in runs:
        record: dict[str, Any] = {
            "label": run["label"],
            "path": run["path"],
            "split": run["results"].get("split"),
            "primary": {},
            "external": run["results"].get("external", {}),
        }
        for target, entries in run["results"].get("primary", {}).items():
            record["primary"][target] = {}
            for feature_set, entry in entries.items():
                best = entry.get("best") or {}
                record["primary"][target][feature_set] = {
                    "model": best.get("model_name"),
                    "val": best.get("val"),
                    "test": best.get("test"),
                    "test_ci": best.get("test_ci"),
                }
        comparison["runs"].append(record)

    (args.out / "comparison.json").write_text(
        json.dumps(comparison, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (args.out / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {args.out / 'comparison.md'}")
    print(f"wrote {args.out / 'comparison.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
