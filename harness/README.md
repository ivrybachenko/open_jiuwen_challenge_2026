# harness

Исходники харнесса. Точка входа — `src/harness/run_agent.py`; `main` живёт
там, а `cli.py` только разбирает аргументы.

## Структура по бизнес-функциям

```
src/harness/
  run_agent.py                  # entrypoint: main + logging
  cli.py                        # только argparse
  config.py                     # Settings, список моделей
  logging_setup.py              # логи openJiuwen до импорта SDK

  tasks/                        # задача и её файлы
    model.py                    # Task, answer.txt
    loader.py                   # чтение task.json

  state/                        # состояние одной задачи
    model.py                    # TaskState
    store.py                    # атомарный state.json

  answers/                      # контракт ответа
    model.py                    # AnswerInfo
    classify.py                 # classify_answer

  attempts/                     # ход как источник данных
    features.py                 # extract_features
    log.py                      # AttemptLogger (JSONL + YAML)

  budget/                       # бюджет и стоимость токенов
    ledger.py                   # token_cost, TokenLedger

  success_predictors/           # вероятность успеха
    heuristic.py                # success_probability
    model.py                    # predict_success
    models/                     # артефакты sklearn-модели
    __init__.py                 # estimate_success: модель -> эвристика

  workspace/                    # работа с каталогом задачи
    overview.py                 # обзор директории
    shell.py                    # процессы с таймаутом и обрезкой вывода

  solutions/                    # итоговый solutions.json
    store.py

  solving/                      # прогон набора задач
    runner.py                   # задачи, волны, solutions.json
    waves.py                    # выбор следующей волны

  agents/                       # выполнение одного хода
    script_agent.py             # ScriptAgent(BaseAgent), SYSTEM_PROMPT
    rails/
      budget.py
      failure.py
      followup.py               # follow-up warning
      answer.py
      features.py
```

Поток одного прогона:

```
cli -> solving.runner
          -> agents.script_agent.invoke
               -> Model.invoke
               -> bash-скрипт в workspace
               -> agents.rails (budget / failure / followup / answer / features)
          -> solving.waves.select
          -> solutions.store.record после каждого хода
```

Пакет = бизнес-функция, а не технический слой:

- `tasks` — что решаем;
- `state` — что помним о задаче между ходами;
- `answers` — что считается ответом;
- `attempts` — что записываем о ходе;
- `budget` — как считаем деньги;
- `success_predictors` — как оцениваем шанс успеха;
- `workspace` — как взаимодействуем с файлами и процессами;
- `solutions` — как отдаём итог;
- `solving` — как гоняем волны;
- `agents` — как выполняется один ход и его lifecycle-rails.

Промпты лежат там, где используются: `SYSTEM_PROMPT` — в
`agents/script_agent.py`, follow-up warning — в `agents/rails/followup.py`.

## Проверка

```bash
uv sync
uv run python -m unittest discover -s test
```

Интеграционный прогон одной задачи:

```bash
LLM_API_KEY="$NEURAL_DEEP_API_KEY" \
  .venv/bin/python -m evaluation.harness_task_checker \
  --task math/solvable/0001
```
