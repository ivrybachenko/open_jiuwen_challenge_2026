# Артефакты эксперимента 0003

Каталог создан скриптами из `research/experiments/0003-reasoning-models-and-explanations/`.

Кратко: `nn-single` (NR в обеих волнах, один полный скрипт без пояснения) —
91 балл из 97 за 14 544 токена; `rr-plain` — 90 за 36 252; `nr-plain` — 85
за 19 506. Разрешённый блок пояснений (`*-explain`) ломает исполнение, потому
что модель дробит ответ на несколько fenced-блоков; требование одного блока
это исправляет, а сам текст пояснения не нужен.

| Файл | Что внутри |
| --- | --- |
| `tasks.yaml` | Зафиксированная стратифицированная выборка 32 задач |
| `results/comparison.md` / `comparison.json` | Сводка по конфигурациям, парам задач и формату ответа |
| `results/comparison.txt` | Тот же отчёт в текстовом виде (вывод `analyze.py`) |
| `results/<config>/summary.json` | Итог конфигурации: балл, стоимость, волны, задачи |
| `results/<config>/tasks.jsonl` | Построчные результаты и статистика волн |
| `results/<config>/harness.log` | Команда, stdout/stderr харнесса |
| `results/<config>/solutions.json` | `solutions.json` харнесса |
| `results/<config>/traj/` | Журнал попыток; в git не хранится |
| `results/<config>/agents/` | Состояния задач и скрипты; в git не хранится |

Полные траектории большие, поэтому `traj/`, `agents/` и `work/` исключены
через `.gitignore`. Их можно пересоздать запуском:

```bash
LLM_API_KEY="$NEURAL_DEEP_API_KEY" \
python research/experiments/0003-reasoning-models-and-explanations/run_experiment.py
python research/experiments/0003-reasoning-models-and-explanations/analyze.py
```

`run_experiment.py` не меняет исходный `data/task`: для каждой конфигурации
он копирует задачи во временный каталог `results/<config>/work/tasks`.

Конфигурации: `rr-plain`, `nr-plain`, `nn-plain` — базовые; `*-explain` —
разрешённый блок пояснений; `*-explain-single` — ровно один fenced-блок с
полным скриптом; `nn-single` — один блок без пояснения (абляция формата);
`route-search-r` — R в первой волне только для `search`.
Волны: R = `qwen3.6-35b-a3b`, NR = `qwen3.6-35b-a3b-noreason`.
