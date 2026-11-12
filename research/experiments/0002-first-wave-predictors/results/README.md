# Артефакты эксперимента 0002

Каталог создан скриптами из `research/experiments/0002-first-wave-predictors/`.
Исходные журналы `data/trajectories/exp0002-shard*/bash_attempts.jsonl` в git
не хранятся (`.gitignore`), но `dataset.csv` и отчёты можно воспроизвести
командами из записи эксперимента.

| Файл | Что внутри |
| --- | --- |
| `comparison.md` / `comparison.json` | Горизонтальное и четыре вертикальных разбиения: метрики, модели, Δ keyword и Δ static |
| `keyword_stats.md` / `keyword_stats.json` | Частоты лексических маркеров и их корреляции с целями |
| `correctness.json` | `task_id -> bool` от answer evaluator для собранного прогона |
| `rule_check.json` | Проверка детерминированного правила для `remaining_turns`: 240 групп, 0 расхождений |
| `correctness_details.json` | Подробные вердикты оценщика |
| `horizontal/` | Обучение и отчёт на горизонтальном разбиении (136/45/59) |
| `vertical-search/` | train coding+data_analysis, val math, test search |
| `vertical-coding/` | train data_analysis+math, val search, test coding |
| `vertical-data-analysis/` | train math+search, val coding, test data_analysis |
| `vertical-math/` | train search+coding, val data_analysis, test math |

В каждом каталоге разбиения:

- `results.json` — все кандидаты, baseline, выбранная модель, bootstrap CI,
  важность признаков (для горизонтального), внешняя проверка;
- `summary.md` — краткая таблица;
- `dataset.csv` — построчный датасет с признаками и целями;
- `external_dataset.csv` — строки более ранних прогонов, попавших в test.
