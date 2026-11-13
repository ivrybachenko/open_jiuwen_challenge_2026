#!/usr/bin/env python3
"""Cross-source check: train on research tasks, test on evaluation tasks.

This is the closest available task-level holdout: the 32 research tasks and the
evaluation tasks come from different task families.  The sample is small, but
it answers whether the per-wave ranking survives a source shift.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from train_wave_models import (
    COLUMNS,
    MODEL_DIR,
    _load_rows,
    _metrics,
    _model,
)

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "cross_source_report.json"


def evaluate_source(
    frame: pd.DataFrame,
    *,
    source: str,
    target_wave: int,
    train_wave: int,
) -> dict:
    train = frame[
        (frame["source_kind"] == source) & (frame["wave"] == train_wave)
    ]
    other = "evaluation" if source == "research" else "research"
    test = frame[
        (frame["source_kind"] == other) & (frame["wave"] == target_wave)
    ].reset_index(drop=True)
    result: dict = {
        "source": source,
        "target_source": other,
        "target_wave": target_wave,
        "train_wave": train_wave,
        "train_rows": int(len(train)),
        "train_tasks": int(train["task_id"].nunique()),
        "test_rows": int(len(test)),
        "test_tasks": int(test["task_id"].nunique()),
        "test_tasks_list": sorted(test["task_id"].unique().tolist()),
        "models": {},
    }
    if len(train) < 8 or len(test) < 3:
        result["skipped"] = "too few rows"
        return result
    y = test["final_correct"].astype(int).to_numpy()
    for kind in ("logreg", "rf", "ensemble"):
        model = _model(kind)
        model.fit(train[COLUMNS], train["final_correct"].astype(int))
        probability = model.predict_proba(test[COLUMNS])[:, 1]
        result["models"][kind] = _metrics(y, probability)

    global_model = joblib.load(MODEL_DIR / "online_correct_model.joblib")
    global_probability = global_model.predict_proba(test[COLUMNS])[:, 1]
    result["models"]["global"] = _metrics(y, global_probability)
    return result


def main() -> int:
    frame = _load_rows()
    report = {"target": "train on one source, test on the other"}
    for target_wave, train_wave in ((2, 2), (3, 2), (4, 4)):
        report[f"research_to_evaluation_wave{target_wave}"] = evaluate_source(
            frame,
            source="research",
            target_wave=target_wave,
            train_wave=train_wave,
        )
        report[f"evaluation_to_research_wave{target_wave}"] = evaluate_source(
            frame,
            source="evaluation",
            target_wave=target_wave,
            train_wave=train_wave,
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    for name, result in report.items():
        if not isinstance(result, dict) or "models" not in result:
            continue
        print(
            f"\n=== {name}: train {result['train_rows']} rows/"
            f"{result['train_tasks']} tasks -> test {result['test_rows']} rows/"
            f"{result['test_tasks']} tasks {result['test_tasks_list']}"
        )
        for kind, metrics in result["models"].items():
            auc = metrics["auc"]
            print(
                f"  {kind:9s} n={metrics['n']:3d} "
                f"AUC={auc if auc is None else round(auc, 3)} "
                f"Brier={metrics['brier']:.3f} "
                f"meanP={metrics['mean_prediction']:.3f} "
                f"rate={metrics['base_rate']:.3f}"
            )
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
