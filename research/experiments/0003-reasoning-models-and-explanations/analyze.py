#!/usr/bin/env python3
"""Build a comparison report for experiment 0003 from ``results/*/summary.json``."""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import defaultdict
from math import comb
from pathlib import Path
from statistics import mean, median
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=SCRIPT_DIR / "results")
    parser.add_argument("--out", type=Path, default=None)
    return parser.parse_args(argv)


def _load(results_dir: Path) -> list[dict[str, Any]]:
    payloads = []
    for path in sorted(results_dir.glob("*/summary.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["_dir"] = str(path.parent)
        payloads.append(payload)
    return payloads


def _task_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["task_path"]: row for row in payload["tasks"]}


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
    means = []
    for _ in range(samples):
        means.append(mean(values[rng.randrange(n)] for _ in range(n)))
    means.sort()
    return [means[int(0.025 * samples)], means[int(0.975 * samples) - 1]]


def _mcnemar_exact(only_left: int, only_right: int) -> float | None:
    """Two-sided exact McNemar p-value for paired binary outcomes."""
    discordant = only_left + only_right
    if discordant == 0:
        return None
    tail = sum(comb(discordant, i) for i in range(min(only_left, only_right) + 1))
    return min(1.0, 2.0 * tail / (2**discordant))


def _paired(
    left: dict[str, Any],
    right: dict[str, Any],
) -> dict[str, Any]:
    left_tasks = _task_map(left)
    right_tasks = _task_map(right)
    common = sorted(set(left_tasks) & set(right_tasks))
    both = only_left = only_right = neither = 0
    left_costs, right_costs = [], []
    left_scores, right_scores = [], []
    for path in common:
        a = bool(left_tasks[path]["solved"])
        b = bool(right_tasks[path]["solved"])
        if a and b:
            both += 1
        elif a:
            only_left += 1
        elif b:
            only_right += 1
        else:
            neither += 1
        left_costs.append(int(left_tasks[path]["tokens"]["cost"]))
        right_costs.append(int(right_tasks[path]["tokens"]["cost"]))
        left_scores.append(float(left_tasks[path]["score"]))
        right_scores.append(float(right_tasks[path]["score"]))
    cost_diffs = [left - right for left, right in zip(left_costs, right_costs)]
    score_diffs = [left - right for left, right in zip(left_scores, right_scores)]
    return {
        "tasks": len(common),
        "both": both,
        "only_left": only_left,
        "only_right": only_right,
        "neither": neither,
        "mcnemar_p": _mcnemar_exact(only_left, only_right),
        "left_score_sum": sum(left_scores),
        "right_score_sum": sum(right_scores),
        "score_diff_mean": mean(score_diffs) if score_diffs else 0,
        "score_diff_ci": _bootstrap_mean_ci(score_diffs),
        "left_cost_sum": sum(left_costs),
        "right_cost_sum": sum(right_costs),
        "left_cost_median": median(left_costs) if left_costs else 0,
        "right_cost_median": median(right_costs) if right_costs else 0,
        "cost_diff_mean": mean(cost_diffs) if cost_diffs else 0,
        "cost_diff_median": median(cost_diffs) if cost_diffs else 0,
        "cost_diff_ci": _bootstrap_mean_ci(cost_diffs),
    }


def _group_rows(rows: list[dict[str, Any]]) -> dict[str, float]:
    def wave_cost(row: dict[str, Any], wave: str) -> int:
        return int((row.get(wave) or {}).get("cost") or 0)

    def wave_answered(row: dict[str, Any], wave: str) -> bool:
        kind = (row.get(wave) or {}).get("answer_kind")
        return kind in {"done", "value"}

    return {
        "tasks": len(rows),
        "solved": sum(1 for row in rows if row["solved"]),
        "score": sum(float(row["score"]) for row in rows),
        "cost": sum(int(row["tokens"]["cost"]) for row in rows),
        "wave1_answered": sum(1 for row in rows if wave_answered(row, "wave1")),
        "wave1_closed": sum(1 for row in rows if row["wave1_closed"]),
        "wave2_closed": sum(1 for row in rows if row["wave2_closed"]),
        "wave1_cost": sum(wave_cost(row, "wave1") for row in rows),
        "wave2_cost": sum(wave_cost(row, "wave2") for row in rows),
    }


def _category_rows(payload: dict[str, Any]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in payload["tasks"]:
        grouped[row["task_type"]].append(row)
    return {category: _group_rows(rows) for category, rows in sorted(grouped.items())}


def _solvable_rows(payload: dict[str, Any]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in payload["tasks"]:
        grouped["solvable" if row.get("solvable") else "impossible"].append(row)
    return {name: _group_rows(rows) for name, rows in sorted(grouped.items())}


_FENCE_RE = re.compile(
    r"```(?:bash|sh|shell|zsh)?[ \t]*\r?\n.*?```", re.IGNORECASE | re.DOTALL
)


def _explanation_chars(content: str) -> int:
    if not _FENCE_RE.search(content):
        return 0
    return len("".join(_FENCE_RE.sub("", content).split()))


def _trajectory_stats(payload: dict[str, Any]) -> dict[str, Any]:
    path = Path(payload["_dir"]) / "traj" / "bash_attempts.jsonl"
    try:
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except OSError:
        return {}
    result = {}
    for wave in (1, 2):
        wave_records = [record for record in records if record.get("wave") == wave]
        if not wave_records:
            result[f"wave{wave}"] = None
            continue
        blocks = [
            str(record.get("content") or "").count("```") // 2
            for record in wave_records
        ]
        scripts = [str(record.get("script") or "").strip() for record in wave_records]
        with_explanation = sum(
            1
            for record in wave_records
            if _explanation_chars(str(record.get("content") or "")) > 0
        )
        short_script = sum(
            1
            for record in wave_records
            if len(str(record.get("script") or "").strip()) < 40
            and len(str(record.get("content") or "")) > 200
        )
        echo_done = sum(
            1
            for script in scripts
            if script in {'echo "DONE" > answer.txt', "echo DONE > answer.txt"}
        )
        result[f"wave{wave}"] = {
            "turns": len(wave_records),
            "with_explanation": with_explanation,
            "median_blocks": median(blocks),
            "single_block": sum(1 for count in blocks if count == 1),
            "multi_block": sum(1 for count in blocks if count > 1),
            "short_script_after_long_reply": short_script,
            "echo_done_only": echo_done,
        }
    return result


def _fmt(value: float) -> str:
    if isinstance(value, float):
        return f"{value:.3g}"
    return str(value)


def build_report(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    by_name = {payload["config"]["name"]: payload for payload in payloads}
    configs = []
    for payload in payloads:
        summary = payload["summary"]
        waves = payload["waves"]
        solved = summary["solved_tasks"] or 0
        configs.append(
            {
                "name": payload["config"]["name"],
                "wave1_model": payload["config"]["wave1_model"],
                "wave2_model": payload["config"]["wave2_model"],
                "explain": payload["config"]["explain"],
                "explain_mode": payload["config"].get(
                    "explain_mode",
                    "allowed" if payload["config"]["explain"] else "off",
                ),
                "score": summary["score"],
                "solved": solved,
                "tasks": summary["total_tasks"],
                "cost": summary["cost"],
                "cost_per_solved": (summary["cost"] / solved) if solved else None,
                "score_per_1k_tokens": (
                    summary["score"] * 1000.0 / summary["cost"] if summary["cost"] else None
                ),
                "wave1_cost": waves["wave1"]["cost"],
                "wave1_answered": waves["wave1"]["answered_tasks"],
                "wave1_hit_limit": waves["wave1"]["hit_token_limit"],
                "wave1_reasoning_tokens": waves["wave1"]["reasoning_tokens"],
                "wave1_with_explanation": waves["wave1"]["with_explanation"],
                "wave2_tasks": waves["wave2"]["tasks"],
                "wave2_answered": waves["wave2"]["answered"],
                "wave2_cost": waves["wave2"]["cost"],
                "wave2_reasoning_tokens": waves["wave2"]["reasoning_tokens"],
                "wave2_with_explanation": waves["wave2"]["with_explanation"],
                "duration_seconds": payload["duration_seconds"],
                "returncode": payload["returncode"],
                "categories": _category_rows(payload),
                "solvability": _solvable_rows(payload),
                "trajectory": _trajectory_stats(payload),
            }
        )

    pairs = []
    comparisons = [
        ("rr-plain", "nr-plain"),
        ("nr-plain", "nn-plain"),
        ("rr-plain", "rr-explain"),
        ("nr-plain", "nr-explain"),
        ("nn-plain", "nn-explain"),
        ("rr-explain", "nr-explain"),
        ("nn-explain", "nr-explain"),
        ("rr-plain", "nn-plain"),
        ("rr-plain", "rr-explain-single"),
        ("nr-plain", "nr-explain-single"),
        ("nn-plain", "nn-explain-single"),
        ("rr-explain", "rr-explain-single"),
        ("nr-explain", "nr-explain-single"),
        ("rr-explain-single", "nr-explain-single"),
        ("nr-explain-single", "nn-explain-single"),
        ("rr-plain", "route-search-r"),
        ("nr-plain", "route-search-r"),
        ("route-search-r", "nn-plain"),
        ("rr-plain", "nn-explain-single"),
        ("nr-plain", "nn-explain-single"),
        ("rr-plain", "nr-explain-single"),
        ("rr-explain-single", "nn-explain-single"),
        ("nn-explain-single", "route-search-r"),
        ("nn-plain", "nn-single"),
        ("nn-single", "nn-explain-single"),
        ("nr-plain", "nn-single"),
        ("rr-plain", "nn-single"),
    ]
    for left, right in comparisons:
        if left in by_name and right in by_name:
            pairs.append(
                {"left": left, "right": right, **_paired(by_name[left], by_name[right])}
            )
    achievable = None
    if payloads:
        achievable = sum(
            float(row["reward"])
            for row in payloads[0]["tasks"]
            if row.get("solvable")
        )
    return {"configs": configs, "pairs": pairs, "achievable_max_score": achievable}


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# Experiment 0003: comparison", ""]
    achievable = report.get("achievable_max_score")
    if achievable:
        lines.append(
            f"> `max_score` в `summary.json` включает reward нерешаемых задач; "
            f"реально достижимый максимум — {achievable:g} по решаемым задачам."
        )
        lines.append("")
    lines.append("## Configurations")
    lines.append("")
    lines.append(
        "| config | wave1 | wave2 | explain | score | solved | cost | cost/solved | "
        "score/1k tok | wave1 cost | wave1 answered | wave2 cost | wave2 answered |"
    )
    lines.append("| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for item in report["configs"]:
        cps = "-" if item["cost_per_solved"] is None else f"{item['cost_per_solved']:.0f}"
        spt = (
            "-"
            if item["score_per_1k_tokens"] is None
            else f"{item['score_per_1k_tokens']:.2f}"
        )
        lines.append(
            f"| {item['name']} | {item['wave1_model'].removesuffix('-noreason')} | "
            f"{item['wave2_model'].removesuffix('-noreason')} | "
            f"{item['explain_mode']} | {item['score']:g} | "
            f"{item['solved']}/{item['tasks']} | {item['cost']} | {cps} | {spt} | "
            f"{item['wave1_cost']} | {item['wave1_answered']} | "
            f"{item['wave2_cost']} | {item['wave2_answered']} |"
        )

    lines += ["", "## Wave behaviour", ""]
    lines.append(
        "| config | wave1 hit limit | wave1 reasoning tok | wave1 w/ explanation | "
        "wave2 tasks | wave2 reasoning tok | wave2 w/ explanation |"
    )
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for item in report["configs"]:
        lines.append(
            f"| {item['name']} | {item['wave1_hit_limit']} | "
            f"{item['wave1_reasoning_tokens']} | {item['wave1_with_explanation']} | "
            f"{item['wave2_tasks']} | {item['wave2_reasoning_tokens']} | "
            f"{item['wave2_with_explanation']} |"
        )

    lines += ["", "## Reply format", ""]
    lines.append(
        "`multi-block` — ответ содержал больше одного fenced-блока; "
        "`short script` — исполняемый скрипт короче 40 символов при длинном "
        "ответе; `echo DONE` — скрипт состоял только из записи DONE."
    )
    lines.append("")
    lines.append(
        "| config | wave | turns | with explanation | median blocks | single block | "
        "multi-block | short script | echo DONE only |"
    )
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for item in report["configs"]:
        for wave in (1, 2):
            stats = (item.get("trajectory") or {}).get(f"wave{wave}")
            if not stats:
                continue
            lines.append(
                f"| {item['name']} | {wave} | {stats['turns']} | "
                f"{stats['with_explanation']} | {stats['median_blocks']:g} | "
                f"{stats['single_block']} | {stats['multi_block']} | "
                f"{stats['short_script_after_long_reply']} | {stats['echo_done_only']} |"
            )

    lines += ["", "## Paired task comparison", ""]
    lines.append(
        "`only left` — задача решена только в левом конфиге, `only right` — только "
        "в правом; `cost` — суммарная стоимость общих задач."
    )
    lines.append("")
    lines.append(
        "| left | right | tasks | both | only left | only right | neither | "
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
            f"| {pair['left']} | {pair['right']} | {pair['tasks']} | {pair['both']} | "
            f"{pair['only_left']} | {pair['only_right']} | {pair['neither']} | "
            f"{p_text} | {score_text} | {cost_text} |"
        )

    lines += ["", "## By solvability", ""]
    lines.append(
        "| config | group | tasks | solved | score | cost | wave1 answered | "
        "wave1 closed | wave2 closed | wave1 cost | wave2 cost |"
    )
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for item in report["configs"]:
        for group in ("solvable", "impossible"):
            row = item["solvability"].get(group)
            if not row:
                continue
            lines.append(
                f"| {item['name']} | {group} | {row['tasks']} | {row['solved']} | "
                f"{row['score']:g} | {row['cost']} | {row['wave1_answered']} | "
                f"{row['wave1_closed']} | {row['wave2_closed']} | "
                f"{row['wave1_cost']} | {row['wave2_cost']} |"
            )

    lines += ["", "## By category", ""]
    categories = sorted(
        {cat for item in report["configs"] for cat in item["categories"]}
    )
    for category in categories:
        lines += [f"### {category}", ""]
        lines.append("| config | solved | score | cost | wave1 closed | wave2 closed |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
        for item in report["configs"]:
            row = item["categories"].get(category)
            if not row:
                continue
            lines.append(
                f"| {item['name']} | {row['solved']}/{row['tasks']} | {row['score']:g} | "
                f"{row['cost']} | {row['wave1_closed']} | {row['wave2_closed']} |"
            )
        lines.append("")
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
