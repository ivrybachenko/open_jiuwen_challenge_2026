# Артефакты статического предиктора (0006)

Все модели обучены на 240 задачах `data/task` и стоимости свежего прогона
`0003` (одна попытка на задачу, две волны). Признаки — только доступные до
первого хода: инструкция, workspace, категория, `reward` и обзор, который
харнесс строит перед первым вызовом.

| Файл | Что это |
| --- | --- |
| `predictor.json` | список признаков, цели и описание моделей |
| `cost_model.joblib` | `Pipeline(ColumnTransformer, RandomForestRegressor)`, цель `log1p(средняя суммарная стоимость)` |
| `correct_model.joblib` | вероятность правильного ответа до решения |
| `impossible_model.joblib` | вероятность метки `impossible` |
| `answered_model.joblib` | вероятность ответа в первой волне (двухстадийная модель) |
| `cost_answered_model.joblib` | стоимость волны 1 при условии ответа |
| `cost_unanswered_model.joblib` | полная стоимость при отсутствии ответа |
| `linear_cost_model.json` | Ridge-экспорт без зависимости от sklearn: коэффициенты, импутация, масштаб, one-hot |
| `static_features.csv` | структурные признаки всех 240 задач |
| `static_features_leak.csv` | те же признаки + `check`/`expected`/`solvable` (только для замера утечки) |
| `overview_features.csv` | длина обзора и сигналы тестов, агрегированные по задачам |
| `current_runs.csv` | сырые стоимости 240 задач |
| `example_runs.csv` | 8 задач организаторов |
| `static_predictions.csv` | out-of-fold предсказания для random-разбиения |
| `static_report.json`, `classification_report.json` | метрики и важность признаков |

## Как получить предсказание

```python
import json
import joblib
import pandas as pd
from pathlib import Path

here = Path("research/experiments/0006-predict-cost-before-solve/results")
meta = json.loads((here / "predictor.json").read_text())
features = pd.read_csv(here / "static_features.csv")
overview = pd.read_csv(here / "overview_features.csv")
row = features.merge(overview, on="rel").head(1)

cost_model = joblib.load(here / "cost_model.joblib")
log_cost = cost_model.predict(row[meta["features"]])[0]
print("expected tokens:", float(__import__("math").expm1(log_cost)))
```

Для рантайма признаки надо собрать тем же кодом, что в
`static_features.py`. Скрытый набор, скорее всего, плоский
(`<task_id>/task.json`), поэтому используйте:

```bash
python static_features.py --tasks-dir /data/tasks --with-overview --out features.csv
```

`--with-overview` вызывает тот же `build_overview`, что и харнесс (включая
запуск тестов), и добавляет `overview_*`/`tests_in_overview`. Стоимость
обзора уже входит в первый вызов.

## Ограничения

- Абсолютная стоимость смещена: MAE 188 против 204 у медианы категории,
  Spearman 0,42. На 8 задачах организаторов MAE 192 против 86 у медианы
  категории. Перед использованием на скрытом наборе нужна калибровка
  (сдвиг/масштаб по логу стоимости) на 3–5 реальных задачах.
- `correct_model.joblib` и `impossible_model.joblib` не переносятся на новый
  блок генератора: AUC 0,32–0,35 на leave-block-out. Использовать только
  как признак ансамбля, не как самостоятельный фильтр.
- Двухстадийная модель (`answered_model` + `cost_answered` +
  `cost_unanswered`) интерпретируема, но хуже прямой: MAE 229 против 188.
  Оставлена для экспериментов, не как основная.
