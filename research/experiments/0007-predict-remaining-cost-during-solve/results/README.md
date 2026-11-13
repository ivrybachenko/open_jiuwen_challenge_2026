# Артефакты онлайн-предиктора (0007)

Модель работает **после первого хода**: на вход идут только признаки,
которые уже есть в `TaskState` (расход, скрипт, вывод, код возврата, вид
ответа, категория, `reward`). Она предсказывает вероятность того, что
итоговый ответ будет зачтён.

| Файл | Что это |
| --- | --- |
| `online_predictor.json` | список признаков, метрики и формула стоимости следующего хода |
| `online_correct_model.joblib` | `Pipeline(ColumnTransformer, RandomForestClassifier)`, цель `correct` |
| `online_fresh_predictions.csv` | out-of-fold предсказания на 240 свежих задачах |
| `turn_groups.csv` | одна строка на (прогон, задача) после первого хода |
| `turn_pairs.csv` | пары «первый → второй ход» |
| `online_report.json` | метрики регрессии и классификации |
| `budget_report_fresh.json` | бюджетная симуляция на свежих задачах |
| `policy_tasks.csv` | предсказания для симуляции на смешанных данных |

## Как получить предсказание

```python
import json
import joblib
import pandas as pd
from pathlib import Path

here = Path("research/experiments/0007-predict-remaining-cost-during-solve/results")
meta = json.loads((here / "online_predictor.json").read_text())
model = joblib.load(here / "online_correct_model.joblib")
groups = pd.read_csv(here / "turn_groups.csv")
row = groups.head(1)  # заменить на строку текущего состояния
p_correct = model.predict_proba(row[meta["numeric_features"] + meta["categorical_features"]])[0, 1]
print("P(correct):", p_correct)
```

Формула стоимости следующего хода из `online_predictor.json`:

```
next_input ≈ prev_input + prev_output + len(script_output) / 4 + 154
```

Она даёт MAE 62 токена (MAPE 4 %); обучаемая Ridge-модель — MAE 33
(MAPE 3,96 %), но формула не требует зависимости от sklearn.

## Ограничения

- Обучено на синтетических задачах, один повтор на задачу. На скрытом наборе
  вероятности могут сдвинуться; нужна калибровка на нескольких реальных
  прогонах.
- Предсказывает **вероятность успеха**, а не величину остатка стоимости:
  `remaining_cost` по признакам первого хода не предсказывается (MAE 303
  против 320 у медианы). Для бюджета используйте `cost1 + 230…288`.
- Бюджетная симуляция — офлайн, по залогированным исходам. Живой прогон
  с новой политикой не проводился.
- Наивная перепроверка отвеченных задач с низким `P(correct)` не сработала
  (0/6 в пилоте `0010`); не включать её без нового эксперимента.
