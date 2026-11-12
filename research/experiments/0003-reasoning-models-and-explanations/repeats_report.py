#!/usr/bin/env python3
"""Summarise repeated runs of the key experiment 0003 configurations."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIGS = ("rr-plain", "nr-plain", "nn-plain", "nn-single")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dirs",
        nargs="+",
        type=Path,
        default=[SCRIPT_DIR / "results" / f"repeats-{i}" for i in (1, 2, 3)],
    )
    parser.add_argument(
        "--original",
        type=Path,
        default=SCRIPT_DIR / "results",
        help="Directory with the first run of each config (optional).",
    )
    parser.add_argument(
        "--configs",
        default=",".join(CONFIGS),
        help="Comma-separated config names.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=SCRIPT_DIR / "results" / "repeats-summary.md",
    )
    return parser.parse_args(argv)


def _load(directory: Path, config: str) -> dict[str, Any] | None:
    path = directory / config / "summary.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    payload["_path"] = str(path)
    return payload


def _metric(payload: dict[str, Any]) -> dict[str, float]:
    summary = payload["summary"]
    waves = payload["waves"]
    return {
        "score": float(summary["score"]),
        "solved": float(summary["solved_tasks"]),
        "tasks": float(summary["total_tasks"]),
        "cost": float(summary["cost"]),
        "wave1_cost": float(waves["wave1"]["cost"]),
        "wave2_cost": float(waves["wave2"]["cost"]),
        "seconds": float(payload.get("duration_seconds") or 0.0),
    }


def _stats(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"n": 0, "mean": None, "sd": None, "min": None, "max": None}
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "sd": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def _fmt(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "-"
    return f"{value:.{digits}f}"


def build_report(
    dirs: list[Path],
    original: Path | None,
    configs: list[str],
) -> dict[str, Any]:
    report: dict[str, Any] = {"configs": {}, "dirs": [str(d) for d in dirs]}
    for config in configs:
        runs: list[dict[str, Any]] = []
        if original is not None:
            payload = _load(original, config)
            if payload is not None:
                runs.append({"name": "original", **payload, **{"_metrics": _metric(payload)}})
        for index, directory in enumerate(dirs, start=1):
            payload = _load(directory, config)
            if payload is not None:
                runs.append({"name": f"repeat-{index}", **payload, **{"_metrics": _metric(payload)}})

        metrics = [run["_metrics"] for run in runs]
        summary = {
            key: _stats([item[key] for item in metrics])
            for key in ("score", "solved", "cost", "wave1_cost", "wave2_cost", "seconds")
        }
        report["configs"][config] = {
            "runs": [
                {
                    "name": run["name"],
                    "score": run["_metrics"]["score"],
                    "solved": run["_metrics"]["solved"],
                    "tasks": run["_metrics"]["tasks"],
                    "cost": run["_metrics"]["cost"],
                    "wave1_cost": run["_metrics"]["wave1_cost"],
                    "wave2_cost": run["_metrics"]["wave2_cost"],
                    "seconds": run["_metrics"]["seconds"],
                    "path": run.get("_path"),
                }
                for run in runs
            ],
            "summary": summary,
        }
    return report


def render(report: dict[str, Any]) -> str:
    lines = ["# Experiment 0003: repeated runs", ""]
    lines.append(
        "Повторы ключевых конфигураций на том же наборе 32 задач. "
        "`original` — первый прогон, `repeat-N` — независимые повторы. "
        "Сырой `max_score` — 137, но 8 нерешаемых задач не дают баллов; "
        "реально достижимый максимум — 97."
    )
    lines.append("")
    lines.append("## Runs")
    lines.append("")
    lines.append("| config | run | score | solved | cost | wave1 cost | wave2 cost | time, s |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for config, data in report["configs"].items():
        for run in data["runs"]:
            lines.append(
                f"| {config} | {run['name']} | {run['score']:g} | "
                f"{run['solved']:g}/{run['tasks']:g} | {run['cost']:g} | "
                f"{run['wave1_cost']:g} | {run['wave2_cost']:g} | "
                f"{run['seconds']:.1f} |"
            )
    lines += ["", "## Mean and spread", ""]
    lines.append(
        "| config | n | score mean ± sd (min–max) | solved mean | "
        "cost mean ± sd (min–max) | wave1 cost | wave2 cost |"
    )
    lines.append("| --- | ---: | --- | ---: | --- | ---: | ---: |")
    for config, data in report["configs"].items():
        s = data["summary"]
        score = s["score"]
        cost = s["cost"]
        lines.append(
            f"| {config} | {score['n']} | "
            f"{_fmt(score['mean'], 2)} ± {_fmt(score['sd'], 2)} "
            f"({_fmt(score['min'], 0)}–{_fmt(score['max'], 0)}) | "
            f"{_fmt(s['solved']['mean'], 1)} | "
            f"{_fmt(cost['mean'], 0)} ± {_fmt(cost['sd'], 0)} "
            f"({_fmt(cost['min'], 0)}–{_fmt(cost['max'], 0)}) | "
            f"{_fmt(s['wave1_cost']['mean'], 0)} | "
            f"{_fmt(s['wave2_cost']['mean'], 0)} |"
        )
    lines.append("")
    lines.append("## Reading")
    lines.append("")
    lines.append(
        "Сравнивайте средние и разброс, а не отдельный прогон. Если интервалы "
        "`mean ± sd` у конфигураций пересекаются, разница в баллах не "
        "устойчива; стоимость менее шумная и обычно разделяется чётко."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    configs = [name.strip() for name in args.configs.split(",") if name.strip()]
    report = build_report(args.dirs, args.original, configs)
    text = render(report)
    args.out.write_text(text + "\n", encoding="utf-8")
    json_path = args.out.with_suffix(".json")
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(text)
    print(f"\nwrote {args.out} and {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
