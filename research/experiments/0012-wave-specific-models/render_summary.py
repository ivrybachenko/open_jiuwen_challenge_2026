#!/usr/bin/env python3
"""Render ``report.json`` as a human-readable ``summary.md``."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPORT = HERE / "results" / "report.json"
OUT = HERE / "results" / "summary.md"


def _fmt(value, digits: int = 3) -> str:
    if value is None:
        return "—"
    return f"{value:.{digits}f}"


def main() -> int:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    lines: list[str] = []
    add = lines.append

    add("# 0012: сводка измерений")
    add("")
    add("Данные: `report.json`, `turns.csv`, `build_dataset.py`, `analyze.py`.")
    add("")

    data = report["data"]
    add("## Данные")
    add("")
    add(f"- ходов: {data['turns']}")
    add(f"- решений «продолжать или нет»: {data['candidate_decision_rows']}")
    add(f"- задач: {data['tasks']}; прогонов: {data['runs']}")
    add("")
    add("| Волна | Строк | Задач | Доля успеха |")
    add("| ---: | ---: | ---: | ---: |")
    for wave, row in sorted(data["by_wave"].items(), key=lambda item: int(item[0])):
        add(
            f"| {wave} | {row['rows']} | {row['tasks']} | "
            f"{row['base_rate']:.3f} |"
        )
    add("")

    add("## Качество на отложенных задачах")
    add("")
    add(
        "`wave1` — модель, обученная на первой волне; `same` — на той же волне; "
        "`previous` — на предыдущей; `shipped` — текущая модель харнесса. "
        "Все строки — кандидаты после волны, где харнесс решает, продолжать ли."
    )
    add("")
    for kind in ("logreg", "rf"):
        add(f"### {kind}")
        add("")
        add("| Волна | Модель | n | ROC-AUC | 95 % CI | Brier | ECE | Средняя P | Доля успеха |")
        add("| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |")
        for wave, rows in sorted(
            report["comparisons"].items(), key=lambda item: int(item[0])
        ):
            for name, metrics in rows.items():
                if not name.startswith(kind + ":"):
                    continue
                ci = metrics.get("auc_ci95") or [None, None]
                ci_text = (
                    f"[{ci[0]:.3f}; {ci[1]:.3f}]"
                    if ci[0] is not None
                    else "—"
                )
                add(
                    f"| {wave} | {name.split(':', 1)[1]} | {metrics['n']} | "
                    f"{_fmt(metrics['auc'])} | {ci_text} | "
                    f"{_fmt(metrics['brier'])} | {_fmt(metrics['ece'])} | "
                    f"{_fmt(metrics['mean_prediction'])} | "
                    f"{_fmt(metrics['base_rate'])} |"
                )
        add("")

    add("### Текущая модель харнесса")
    add("")
    add("| Волна | n | ROC-AUC | 95 % CI | Brier | ECE | Средняя P | Доля успеха |")
    add("| ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |")
    for wave, rows in sorted(
        report["comparisons"].items(), key=lambda item: int(item[0])
    ):
        metrics = rows.get("shipped_model")
        if not metrics:
            continue
        ci = metrics.get("auc_ci95") or [None, None]
        ci_text = (
            f"[{ci[0]:.3f}; {ci[1]:.3f}]" if ci[0] is not None else "—"
        )
        add(
            f"| {wave} | {metrics['n']} | {_fmt(metrics['auc'])} | {ci_text} | "
            f"{_fmt(metrics['brier'])} | {_fmt(metrics['ece'])} | "
            f"{_fmt(metrics['mean_prediction'])} | {_fmt(metrics['base_rate'])} |"
        )
    add("")

    add("## Полезность выбора (верхняя половина кандидатов)")
    add("")
    add(
        "Баллы на 1k токенов следующего хода. Сортировка — `P · reward / cost`, "
        "как в харнессе; oracle — по фактическому `reward · correct / cost`."
    )
    add("")
    add("| Волна | Модель | Баллы/1k | Oracle/1k | Все кандидаты/1k |")
    add("| ---: | --- | ---: | ---: | ---: |")
    for wave, rows in sorted(
        report["comparisons"].items(), key=lambda item: int(item[0])
    ):
        for name, metrics in rows.items():
            utility = metrics.get("utility")
            if not utility:
                continue
            add(
                f"| {wave} | {name} | "
                f"{_fmt(utility['policy_score_per_1k'])} | "
                f"{_fmt(utility['oracle_score_per_1k'])} | "
                f"{_fmt(utility['all_score_per_1k'])} |"
            )
    add("")

    add("## Что видно")
    add("")
    add(
        "- На первой волне модель различает кандидатов слабо: ROC-AUC 0,48–0,54. "
        "Это не противоречит 0,90 из `0007`: там AUC считается по всем задачам, "
        "включая уже отвеченные, а решение принимается только по кандидатам."
    )
    add(
        "- На второй и третьей волнах текущая модель и модель первой волны "
        "ранжируют кандидатов около случайного (AUC 0,27–0,44), а модель, "
        "обученная на той же волне, даёт 0,53–0,65 и заметно лучше "
        "калибрована (Brier/ECE)."
    )
    add(
        "- Отдельная модель на волне почти достигает oracle по полезности "
        "выбора на второй волне (15,78 против 15,96 баллов/1k), тогда как "
        "текущая модель — 12,85."
    )
    add(
        "- Выборка мала (75/57/31 строка; 11/9/7 задач на волнах 2/3/4), "
        "интервалы широкие. Это пилот, а не доказательство на скрытом наборе."
    )
    add("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
