#!/usr/bin/env python3
"""Build the comparison report for experiment 0004."""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from math import comb
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=SCRIPT_DIR / "results")
    parser.add_argument("--out", type=Path, default=None)
    return parser.parse_args(argv)


def _load(results_dir: Path) -> list[dict[str, Any]]:
    payloads = []
    for path in sorted(results_dir.glob("*/run-*/summary.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["_dir"] = str(path.parent)
        payloads.append(payload)
    return payloads


def _by_config(payloads: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for payload in payloads:
        grouped[payload["config"]["name"]].append(payload)
    for items in grouped.values():
        items.sort(key=lambda item: item.get("repeat", 0))
    return dict(grouped)


def _bootstrap_mean_ci(
    values: list[float],
    *,
    seed: int = 20261112,
    samples: int = 2000,
) -> list[float] | None:
    if not values:
        return None
    rng = random.Random(seed)
    n = len(values)
    means = [mean(values[rng.randrange(n)] for _ in range(n)) for _ in range(samples)]
    means.sort()
    return [means[int(0.025 * samples)], means[int(0.975 * samples) - 1]]


def _mcnemar_exact(only_left: int, only_right: int) -> float | None:
    discordant = only_left + only_right
    if discordant == 0:
        return None
    tail = sum(comb(discordant, i) for i in range(min(only_left, only_right) + 1))
    return min(1.0, 2.0 * tail / (2**discordant))


def _mean_sd(values: list[float]) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    return (mean(values), pstdev(values) if len(values) > 1 else 0.0)


def _task_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["task_path"]: row for row in payload["tasks"]}


def _cost(row: dict[str, Any]) -> int:
    return int((row.get("tokens") or {}).get("cost") or 0)


def _wave_cost(row: dict[str, Any], wave: str) -> int:
    return int((row.get(wave) or {}).get("cost") or 0)


def _unanswered_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in payload["tasks"] if row.get("wave1_unanswered")]


def _script_feature_means(rows: list[dict[str, Any]], key: str) -> float:
    values = [
        float((row.get("wave1") or {}).get(key) or 0)
        for row in rows
        if row.get("wave1")
    ]
    return mean(values) if values else 0.0


def _point_biserial(rows: list[dict[str, Any]], feature: str) -> float | None:
    xs = []
    ys = []
    for row in rows:
        wave1 = row.get("wave1")
        if not wave1:
            continue
        xs.append(float(wave1.get(feature) or 0))
        ys.append(1.0 if row.get("wave2_solved") else 0.0)
    if len(xs) < 3 or len(set(ys)) < 2:
        return None
    mx, my = mean(xs), mean(ys)
    numerator = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denominator = (
        sum((x - mx) ** 2 for x in xs) ** 0.5
        * sum((y - my) ** 2 for y in ys) ** 0.5
    )
    return numerator / denominator if denominator else None


def _config_summary(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [float(p["summary"]["score"]) for p in payloads]
    solved = [float(p["summary"]["solved_tasks"]) for p in payloads]
    costs = [float(p["summary"]["cost"]) for p in payloads]
    wave1_costs = [float(p["waves"]["wave1"]["cost"]) for p in payloads]
    wave2_costs = [float(p["waves"]["wave2"]["cost"]) for p in payloads]
    wave1_answered = [
        float(p["waves"]["wave1"]["answered_tasks"]) for p in payloads
    ]
    unanswered = [
        row for p in payloads for row in _unanswered_rows(p)
    ]
    attempted = [row for row in unanswered if row.get("wave2")]
    solved_after = [row for row in unanswered if row.get("wave2_solved")]
    return {
        "runs": len(payloads),
        "score_mean": mean(scores) if scores else 0,
        "score_sd": pstdev(scores) if len(scores) > 1 else 0,
        "solved_mean": mean(solved) if solved else 0,
        "solved_sd": pstdev(solved) if len(solved) > 1 else 0,
        "tasks": payloads[0]["summary"]["total_tasks"] if payloads else 0,
        "cost_mean": mean(costs) if costs else 0,
        "cost_sd": pstdev(costs) if len(costs) > 1 else 0,
        "wave1_cost_mean": mean(wave1_costs) if wave1_costs else 0,
        "wave2_cost_mean": mean(wave2_costs) if wave2_costs else 0,
        "wave1_answered_mean": mean(wave1_answered) if wave1_answered else 0,
        "unanswered": len(unanswered),
        "wave2_attempted": len(attempted),
        "wave2_solved": len(solved_after),
        "wave2_conversion": (len(solved_after) / len(unanswered)) if unanswered else None,
        "wave2_conversion_attempted": (
            len(solved_after) / len(attempted) if attempted else None
        ),
        "unanswered_wave1_script_chars": _script_feature_means(unanswered, "script_chars"),
        "unanswered_wave1_script_lines": _script_feature_means(unanswered, "script_lines"),
        "unanswered_wave1_output_chars": _script_feature_means(unanswered, "output_chars"),
        "unanswered_wave1_head_tail": _script_feature_means(unanswered, "has_head_tail"),
        "unanswered_wave1_cat": _script_feature_means(unanswered, "has_cat"),
        "corr_output_wave2_success": _point_biserial(unanswered, "output_chars"),
        "corr_script_lines_wave2_success": _point_biserial(unanswered, "script_lines"),
    }


def _paired(
    left: list[dict[str, Any]], right: list[dict[str, Any]]
) -> dict[str, Any]:
    repeats = min(len(left), len(right))
    left = left[:repeats]
    right = right[:repeats]
    task_rows: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: {"left": [], "right": []}
    )
    only_left = only_right = both = neither = 0
    for left_run, right_run in zip(left, right):
        left_tasks = _task_map(left_run)
        right_tasks = _task_map(right_run)
        for path in sorted(set(left_tasks) & set(right_tasks)):
            a = left_tasks[path]
            b = right_tasks[path]
            task_rows[path]["left"].append(a)
            task_rows[path]["right"].append(b)
            sa = bool(a.get("solved"))
            sb = bool(b.get("solved"))
            if sa and sb:
                both += 1
            elif sa:
                only_left += 1
            elif sb:
                only_right += 1
            else:
                neither += 1
    score_diffs = []
    cost_diffs = []
    for entry in task_rows.values():
        left_score = mean(float(row.get("score") or 0) for row in entry["left"])
        right_score = mean(float(row.get("score") or 0) for row in entry["right"])
        left_cost = mean(_cost(row) for row in entry["left"])
        right_cost = mean(_cost(row) for row in entry["right"])
        score_diffs.append(left_score - right_score)
        cost_diffs.append(left_cost - right_cost)
    return {
        "runs": repeats,
        "tasks": len(task_rows),
        "both": both,
        "only_left": only_left,
        "only_right": only_right,
        "neither": neither,
        "mcnemar_p": _mcnemar_exact(only_left, only_right),
        "score_diff_mean": mean(score_diffs) if score_diffs else 0,
        "score_diff_ci": _bootstrap_mean_ci(score_diffs),
        "cost_diff_mean": mean(cost_diffs) if cost_diffs else 0,
        "cost_diff_ci": _bootstrap_mean_ci(cost_diffs),
        "left_cost_sum": sum(
            _cost(row) for entry in task_rows.values() for row in entry["left"]
        ),
        "right_cost_sum": sum(
            _cost(row) for entry in task_rows.values() for row in entry["right"]
        ),
        "left_score_sum": sum(
            float(row.get("score") or 0)
            for entry in task_rows.values()
            for row in entry["left"]
        ),
        "right_score_sum": sum(
            float(row.get("score") or 0)
            for entry in task_rows.values()
            for row in entry["right"]
        ),
    }


def _category_table(payloads: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for payload in payloads:
        for row in payload["tasks"]:
            grouped[row["task_type"]].append(row)
    result = {}
    for category, rows in sorted(grouped.items()):
        result[category] = {
            "rows": len(rows),
            "score": sum(float(row.get("score") or 0) for row in rows),
            "solved": sum(1 for row in rows if row.get("solved")),
            "cost": sum(_cost(row) for row in rows),
            "wave1_answered": sum(
                1 for row in rows if row.get("wave1_answered")
            ),
            "wave2_solved": sum(
                1 for row in rows if row.get("wave2_solved")
            ),
        }
    return result


def build_report(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    grouped = _by_config(payloads)
    configs = {
        name: _config_summary(items) for name, items in grouped.items()
    }
    pairs = []
    for base, goal in (
        ("base-nn", "goal-nn"),
        ("base-r", "goal-r"),
        ("base-nn", "base-r"),
        ("goal-nn", "goal-r"),
    ):
        if base in grouped and goal in grouped:
            pairs.append(
                {"left": base, "right": goal, **_paired(grouped[base], grouped[goal])}
            )
    categories = {
        name: _category_table(items) for name, items in grouped.items()
    }
    per_run = [
        {
            "config": payload["config"]["name"],
            "repeat": payload.get("repeat"),
            "score": payload["summary"]["score"],
            "solved": payload["summary"]["solved_tasks"],
            "cost": payload["summary"]["cost"],
            "wave1_cost": payload["waves"]["wave1"]["cost"],
            "wave1_answered": payload["waves"]["wave1"]["answered_tasks"],
            "wave2_cost": payload["waves"]["wave2"]["cost"],
            "duration_seconds": payload.get("duration_seconds"),
            "returncode": payload.get("returncode"),
        }
        for payload in payloads
    ]
    return {
        "configs": configs,
        "pairs": pairs,
        "categories": categories,
        "per_run": per_run,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# Experiment 0004: comparison", ""]
    lines += ["## Configurations (mean ± sd over runs)", ""]
    lines.append(
        "| config | runs | score | solved | cost | wave1 cost | wave1 answered | "
        "wave2 cost | unanswered | wave2 attempted | wave2 solved | conversion |"
    )
    lines.append(
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    )
    for name, item in report["configs"].items():
        conversion = (
            "-"
            if item["wave2_conversion"] is None
            else f"{item['wave2_conversion']:.1%}"
        )
        lines.append(
            f"| {name} | {item['runs']} | "
            f"{item['score_mean']:.2f} ± {item['score_sd']:.2f} | "
            f"{item['solved_mean']:.2f} ± {item['solved_sd']:.2f} | "
            f"{item['cost_mean']:.0f} ± {item['cost_sd']:.0f} | "
            f"{item['wave1_cost_mean']:.0f} | {item['wave1_answered_mean']:.1f} | "
            f"{item['wave2_cost_mean']:.0f} | {item['unanswered']} | "
            f"{item['wave2_attempted']} | {item['wave2_solved']} | {conversion} |"
        )

    lines += ["", "## First-turn data collection on unanswered tasks", ""]
    lines.append(
        "| config | script chars | script lines | output chars | has head/tail | "
        "has cat | corr(output, wave2 success) | corr(lines, wave2 success) |"
    )
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for name, item in report["configs"].items():
        corr_output = (
            "-"
            if item["corr_output_wave2_success"] is None
            else f"{item['corr_output_wave2_success']:+.2f}"
        )
        corr_lines = (
            "-"
            if item["corr_script_lines_wave2_success"] is None
            else f"{item['corr_script_lines_wave2_success']:+.2f}"
        )
        lines.append(
            f"| {name} | {item['unanswered_wave1_script_chars']:.0f} | "
            f"{item['unanswered_wave1_script_lines']:.1f} | "
            f"{item['unanswered_wave1_output_chars']:.0f} | "
            f"{item['unanswered_wave1_head_tail']:.2f} | "
            f"{item['unanswered_wave1_cat']:.2f} | {corr_output} | {corr_lines} |"
        )

    lines += ["", "## Paired task comparison", ""]
    lines.append(
        "`Δ` — средняя разница на задачу по повторам; "
        "`only left/right` — исходы по парам задача-повтор."
    )
    lines.append("")
    lines.append(
        "| left | right | runs | both | only left | only right | neither | "
        "McNemar p | Δ score (mean [95% CI]) | Δ cost (mean [95% CI]) |"
    )
    lines.append(
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    )
    for pair in report["pairs"]:
        p_value = pair["mcnemar_p"]
        p_text = "-" if p_value is None else f"{p_value:.4f}"
        score_ci = pair["score_diff_ci"]
        cost_ci = pair["cost_diff_ci"]
        score_text = (
            "-"
            if score_ci is None
            else f"{pair['score_diff_mean']:+.2f} [{score_ci[0]:+.2f}, {score_ci[1]:+.2f}]"
        )
        cost_text = (
            "-"
            if cost_ci is None
            else f"{pair['cost_diff_mean']:+.0f} [{cost_ci[0]:+.0f}, {cost_ci[1]:+.0f}]"
        )
        lines.append(
            f"| {pair['left']} | {pair['right']} | {pair['runs']} | "
            f"{pair['both']} | {pair['only_left']} | {pair['only_right']} | "
            f"{pair['neither']} | {p_text} | {score_text} | {cost_text} |"
        )

    lines += ["", "## By category (aggregated over runs)", ""]
    categories = sorted(
        {cat for table in report["categories"].values() for cat in table}
    )
    for category in categories:
        lines += [f"### {category}", ""]
        lines.append(
            "| config | task-runs | solved | score | cost | wave1 answered | wave2 solved |"
        )
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        for name, table in report["categories"].items():
            row = table.get(category)
            if not row:
                continue
            lines.append(
                f"| {name} | {row['rows']} | {row['solved']} | {row['score']:g} | "
                f"{row['cost']} | {row['wave1_answered']} | {row['wave2_solved']} |"
            )
        lines.append("")

    lines += ["", "## Per run", ""]
    lines.append(
        "| config | run | score | solved | cost | wave1 cost | wave1 answered | "
        "wave2 cost | duration s | rc |"
    )
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for item in report["per_run"]:
        lines.append(
            f"| {item['config']} | {item['repeat']} | {item['score']:g} | "
            f"{item['solved']} | {item['cost']} | {item['wave1_cost']} | "
            f"{item['wave1_answered']} | {item['wave2_cost']} | "
            f"{item['duration_seconds'] or 0:.1f} | {item['returncode']} |"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payloads = _load(args.results_dir)
    if not payloads:
        raise SystemExit(f"no summary.json under {args.results_dir}")
    report = build_report(payloads)
    out = args.out or (args.results_dir / "comparison.md")
    out.write_text(render_markdown(report) + "\n", encoding="utf-8")
    json_path = args.results_dir / "comparison.json"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(render_markdown(report))
    print(f"\nwrote {out} and {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
