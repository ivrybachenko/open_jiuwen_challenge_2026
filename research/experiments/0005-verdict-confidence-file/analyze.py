#!/usr/bin/env python3
"""Build the comparison and calibration report for experiment 0005."""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from math import comb
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
VERDICTS = {"solved", "not_solved", "impossible"}


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
    values: list[float], *, seed: int = 20261112, samples: int = 2000
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


def parse_verdict(raw: str | None) -> dict[str, Any]:
    if raw is None:
        return {"status": "missing", "verdict": None, "confidence": None}
    lines = [line.strip() for line in raw.replace("\r\n", "\n").split("\n")]
    lines = [line for line in lines if line]
    if not lines:
        return {"status": "missing", "verdict": None, "confidence": None}
    verdict = lines[0].lower()
    if verdict not in VERDICTS:
        return {"status": "malformed", "verdict": None, "confidence": None}
    if len(lines) < 2:
        return {"status": "malformed", "verdict": verdict, "confidence": None}
    try:
        confidence = float(lines[1])
    except ValueError:
        return {"status": "malformed", "verdict": verdict, "confidence": None}
    if not 0.0 <= confidence <= 1.0:
        return {"status": "malformed", "verdict": verdict, "confidence": None}
    return {"status": "valid", "verdict": verdict, "confidence": confidence}


def true_class(row: dict[str, Any]) -> str:
    if not row.get("solvable", True):
        return "impossible"
    return "solved" if row.get("solved") else "not_solved"


def _cost(row: dict[str, Any]) -> int:
    return int((row.get("tokens") or {}).get("cost") or 0)


def _auc(pairs: list[tuple[float, int]]) -> float | None:
    positives = [(score, label) for score, label in pairs if label == 1]
    negatives = [(score, label) for score, label in pairs if label == 0]
    if not positives or not negatives:
        return None
    wins = 0.0
    for score_p, _ in positives:
        for score_n, _ in negatives:
            if score_p > score_n:
                wins += 1.0
            elif score_p == score_n:
                wins += 0.5
    return wins / (len(positives) * len(negatives))


def _ece(pairs: list[tuple[float, int]], bins: int = 10) -> float | None:
    if not pairs:
        return None
    buckets: list[list[tuple[float, int]]] = [[] for _ in range(bins)]
    for confidence, correct in pairs:
        index = min(bins - 1, int(confidence * bins))
        buckets[index].append((confidence, correct))
    total = len(pairs)
    ece = 0.0
    for bucket in buckets:
        if not bucket:
            continue
        avg_confidence = mean(conf for conf, _ in bucket)
        accuracy = mean(label for _, label in bucket)
        ece += len(bucket) / total * abs(avg_confidence - accuracy)
    return ece


def _observation(
    row: dict[str, Any], parsed: dict[str, Any]
) -> dict[str, Any] | None:
    if parsed["status"] != "valid":
        return None
    expected = true_class(row)
    return {
        "verdict": parsed["verdict"],
        "confidence": float(parsed["confidence"]),
        "expected": expected,
        "correct": parsed["verdict"] == expected,
        "task_type": row["task_type"],
        "solved": bool(row.get("solved")),
        "reward": float(row.get("reward") or 0),
        "cost": _cost(row),
        "wave": None,
    }


def _observations(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """wave -> list of observations, where wave 1/2 are turn snapshots."""
    result: dict[str, list[dict[str, Any]]] = {"wave1": [], "wave2": [], "final": []}
    verdicts = payload.get("verdicts") or {}
    for row in payload["tasks"]:
        task_id = row["task_id"]
        raw = verdicts.get(task_id) or {}
        for wave_name, key in (("wave1", "1"), ("wave2", "2")):
            parsed = parse_verdict(raw.get(key))
            observation = _observation(row, parsed)
            if observation:
                observation["wave"] = wave_name
                result[wave_name].append(observation)
        # If the second wave ran, its snapshot is the final state even when the
        # agent forgot to rewrite verdict.txt; the wave-1 file is then stale.
        final_raw = raw.get("2") if row.get("wave2") is not None else raw.get("1")
        parsed = parse_verdict(final_raw)
        observation = _observation(row, parsed)
        if observation:
            observation["wave"] = "final"
            result["final"].append(observation)
    return result


def _format_metrics(observations: list[dict[str, Any]]) -> dict[str, Any]:
    if not observations:
        return {
            "n": 0,
            "accuracy": None,
            "brier": None,
            "brier_constant": None,
            "ece": None,
            "mean_confidence": None,
            "auc_solved_correct": None,
            "solved_precision": None,
            "impossible_recall": None,
            "false_impossible": 0,
            "false_impossible_reward": 0.0,
        }
    correct = [1.0 if item["correct"] else 0.0 for item in observations]
    confidences = [item["confidence"] for item in observations]
    pairs = list(zip(confidences, correct))
    base_rate = mean(correct)
    solved_pairs = [
        (item["confidence"], 1 if item["solved"] else 0)
        for item in observations
        if item["verdict"] == "solved"
    ]
    solved_items = [item for item in observations if item["verdict"] == "solved"]
    impossible_items = [
        item for item in observations if item["expected"] == "impossible"
    ]
    false_impossible = [
        item
        for item in observations
        if item["verdict"] == "impossible" and item["expected"] != "impossible"
    ]
    return {
        "n": len(observations),
        "accuracy": base_rate,
        "brier": mean((confidence - value) ** 2 for confidence, value in pairs),
        "brier_constant": mean((base_rate - value) ** 2 for value in correct),
        "ece": _ece(pairs),
        "mean_confidence": mean(confidences),
        "auc_solved_correct": _auc(solved_pairs),
        "solved_precision": (
            mean(1.0 if item["solved"] else 0.0 for item in solved_items)
            if solved_items
            else None
        ),
        "impossible_recall": (
            mean(
                1.0 if item["verdict"] == "impossible" else 0.0
                for item in impossible_items
            )
            if impossible_items
            else None
        ),
        "false_impossible": len(false_impossible),
        "false_impossible_reward": sum(item["reward"] for item in false_impossible),
    }


def _confusion(observations: list[dict[str, Any]]) -> dict[str, Counter]:
    table: dict[str, Counter] = {
        expected: Counter() for expected in ("solved", "not_solved", "impossible")
    }
    for item in observations:
        table[item["expected"]][item["verdict"]] += 1
    return table


def _confidence_buckets(
    observations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    buckets = [
        ("<0.50", 0.0, 0.5),
        ("0.50-0.80", 0.5, 0.8),
        (">=0.80", 0.8, 1.0001),
    ]
    result = []
    for label, low, high in buckets:
        rows = [
            item for item in observations if low <= item["confidence"] < high
        ]
        result.append(
            {
                "label": label,
                "n": len(rows),
                "accuracy": mean(1.0 if item["correct"] else 0.0 for item in rows)
                if rows
                else None,
                "mean_confidence": mean(item["confidence"] for item in rows)
                if rows
                else None,
            }
        )
    return result


def _compliance(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    totals = Counter()
    for payload in payloads:
        verdicts = payload.get("verdicts") or {}
        for row in payload["tasks"]:
            raw = verdicts.get(row["task_id"]) or {}
            for key in ("1", "2"):
                parsed = parse_verdict(raw.get(key))
                totals[parsed["status"]] += 1
    total = sum(totals.values())
    return {
        "turns": total,
        "valid": totals["valid"],
        "missing": totals["missing"],
        "malformed": totals["malformed"],
        "valid_rate": totals["valid"] / total if total else None,
    }


def _config_summary(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [float(p["summary"]["score"]) for p in payloads]
    solved = [float(p["summary"]["solved_tasks"]) for p in payloads]
    costs = [float(p["summary"]["cost"]) for p in payloads]
    wave1_costs = [float(p["waves"]["wave1"]["cost"]) for p in payloads]
    observations = {"wave1": [], "wave2": [], "final": []}
    for payload in payloads:
        for wave, items in _observations(payload).items():
            observations[wave].extend(items)
    prompted = any(payload["config"].get("verdict") for payload in payloads)
    return {
        "runs": len(payloads),
        "tasks": payloads[0]["summary"]["total_tasks"] if payloads else 0,
        "score_mean": mean(scores) if scores else 0,
        "score_sd": pstdev(scores) if len(scores) > 1 else 0,
        "solved_mean": mean(solved) if solved else 0,
        "cost_mean": mean(costs) if costs else 0,
        "cost_sd": pstdev(costs) if len(costs) > 1 else 0,
        "wave1_cost_mean": mean(wave1_costs) if wave1_costs else 0,
        "compliance": _compliance(payloads) if prompted else None,
        "metrics": {
            wave: _format_metrics(items) for wave, items in observations.items()
        },
        "confusion": {
            wave: _confusion(items) for wave, items in observations.items()
        },
        "buckets": {
            wave: _confidence_buckets(items) for wave, items in observations.items()
        },
    }


def _paired(
    left: list[dict[str, Any]], right: list[dict[str, Any]]
) -> dict[str, Any]:
    repeats = min(len(left), len(right))
    only_left = only_right = both = neither = 0
    task_diffs: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {"score": [], "cost": []}
    )
    for left_run, right_run in zip(left[:repeats], right[:repeats]):
        left_tasks = {row["task_path"]: row for row in left_run["tasks"]}
        right_tasks = {row["task_path"]: row for row in right_run["tasks"]}
        for path in sorted(set(left_tasks) & set(right_tasks)):
            a = left_tasks[path]
            b = right_tasks[path]
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
            task_diffs[path]["score"].append(
                float(a.get("score") or 0) - float(b.get("score") or 0)
            )
            task_diffs[path]["cost"].append(_cost(a) - _cost(b))
    score_diffs = [mean(entry["score"]) for entry in task_diffs.values()]
    cost_diffs = [mean(entry["cost"]) for entry in task_diffs.values()]
    return {
        "runs": repeats,
        "tasks": len(task_diffs),
        "both": both,
        "only_left": only_left,
        "only_right": only_right,
        "neither": neither,
        "mcnemar_p": _mcnemar_exact(only_left, only_right),
        "score_diff_mean": mean(score_diffs) if score_diffs else 0,
        "score_diff_ci": _bootstrap_mean_ci(score_diffs),
        "cost_diff_mean": mean(cost_diffs) if cost_diffs else 0,
        "cost_diff_ci": _bootstrap_mean_ci(cost_diffs),
    }


def build_report(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    grouped = _by_config(payloads)
    configs = {name: _config_summary(items) for name, items in grouped.items()}
    pairs = []
    for base, verdict in (
        ("base-nn", "verdict-nn"),
        ("base-nn", "verdict-hard-nn"),
        ("base-r", "verdict-r"),
        ("verdict-nn", "verdict-r"),
    ):
        if base in grouped and verdict in grouped:
            pairs.append(
                {"left": base, "right": verdict, **_paired(grouped[base], grouped[verdict])}
            )
    per_run = [
        {
            "config": payload["config"]["name"],
            "repeat": payload.get("repeat"),
            "score": payload["summary"]["score"],
            "solved": payload["summary"]["solved_tasks"],
            "cost": payload["summary"]["cost"],
            "wave1_cost": payload["waves"]["wave1"]["cost"],
            "verdicts": len(payload.get("verdicts") or {}),
            "duration_seconds": payload.get("duration_seconds"),
            "returncode": payload.get("returncode"),
        }
        for payload in payloads
    ]
    return {"configs": configs, "pairs": pairs, "per_run": per_run}


def _fmt(value: float | None, digits: int = 3) -> str:
    return "-" if value is None else f"{value:.{digits}f}"


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# Experiment 0005: comparison", ""]
    lines += ["## Configurations (mean ± sd over runs)", ""]
    lines.append(
        "| config | runs | score | solved | cost | wave1 cost | verdict turns | "
        "valid verdicts | missing | malformed |"
    )
    lines.append(
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    )
    for name, item in report["configs"].items():
        compliance = item["compliance"]
        if compliance is None:
            valid_rate = "-"
            turns = "-"
            valid = "-"
            missing = "-"
            malformed = "-"
        else:
            valid_rate = (
                "-"
                if compliance["valid_rate"] is None
                else f"{compliance['valid_rate']:.1%}"
            )
            turns = str(compliance["turns"])
            valid = f"{compliance['valid']} ({valid_rate})"
            missing = str(compliance["missing"])
            malformed = str(compliance["malformed"])
        lines.append(
            f"| {name} | {item['runs']} | "
            f"{item['score_mean']:.2f} ± {item['score_sd']:.2f} | "
            f"{item['solved_mean']:.2f} | {item['cost_mean']:.0f} ± {item['cost_sd']:.0f} | "
            f"{item['wave1_cost_mean']:.0f} | {turns} | "
            f"{valid} | {missing} | {malformed} |"
        )

    lines += ["", "## Verdict accuracy and calibration (final turn)", ""]
    lines.append(
        "| config | n | coverage | accuracy | mean confidence | Brier | Brier constant | ECE | "
        "AUC (solved → correct) | solved precision | impossible recall | false impossible | reward lost |"
    )
    lines.append(
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    )
    for name, item in report["configs"].items():
        metrics = item["metrics"]["final"]
        coverage = (
            metrics["n"] / (item["runs"] * item["tasks"]) if item["tasks"] else None
        )
        lines.append(
            f"| {name} | {metrics['n']} | {_fmt(coverage, 1)} | "
            f"{_fmt(metrics['accuracy'])} | "
            f"{_fmt(metrics['mean_confidence'])} | {_fmt(metrics['brier'])} | "
            f"{_fmt(metrics['brier_constant'])} | {_fmt(metrics['ece'])} | "
            f"{_fmt(metrics['auc_solved_correct'])} | {_fmt(metrics['solved_precision'])} | "
            f"{_fmt(metrics['impossible_recall'])} | {metrics['false_impossible']} | "
            f"{metrics['false_impossible_reward']:g} |"
        )

    lines += ["", "## Per-wave calibration", ""]
    lines.append(
        "| config | wave | n | accuracy | mean confidence | Brier | ECE |"
    )
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: |")
    for name, item in report["configs"].items():
        for wave in ("wave1", "wave2", "final"):
            metrics = item["metrics"][wave]
            if metrics["n"] == 0:
                continue
            lines.append(
                f"| {name} | {wave} | {metrics['n']} | {_fmt(metrics['accuracy'])} | "
                f"{_fmt(metrics['mean_confidence'])} | {_fmt(metrics['brier'])} | "
                f"{_fmt(metrics['ece'])} |"
            )

    lines += ["", "## Confusion matrix (final turn)", ""]
    for name, item in report["configs"].items():
        lines += [f"### {name}", ""]
        lines.append("| expected \\ verdict | solved | not_solved | impossible |")
        lines.append("| --- | ---: | ---: | ---: |")
        for expected in ("solved", "not_solved", "impossible"):
            row = item["confusion"]["final"][expected]
            lines.append(
                f"| {expected} | {row['solved']} | {row['not_solved']} | "
                f"{row['impossible']} |"
            )
        lines.append("")

    lines += ["## Confidence buckets (final turn)", ""]
    lines.append("| config | bucket | n | accuracy | mean confidence |")
    lines.append("| --- | --- | ---: | ---: | ---: |")
    for name, item in report["configs"].items():
        for bucket in item["buckets"]["final"]:
            if not bucket["n"]:
                continue
            lines.append(
                f"| {name} | {bucket['label']} | {bucket['n']} | "
                f"{_fmt(bucket['accuracy'])} | {_fmt(bucket['mean_confidence'])} |"
            )
        lines.append("")

    lines += ["## Paired cost and score", ""]
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

    lines += ["", "## Per run", ""]
    lines.append(
        "| config | run | score | solved | cost | wave1 cost | verdict tasks | "
        "duration s | rc |"
    )
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for item in report["per_run"]:
        lines.append(
            f"| {item['config']} | {item['repeat']} | {item['score']:g} | "
            f"{item['solved']} | {item['cost']} | {item['wave1_cost']} | "
            f"{item['verdicts']} | {item['duration_seconds'] or 0:.1f} | "
            f"{item['returncode']} |"
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
