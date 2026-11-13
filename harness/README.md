# harness

Исходники харнесса. Точка входа — `src/harness/run_agent.py`, она вызывает
`harness.application.cli.main`.

## Структура

```
src/harness/
  run_agent.py              # entrypoint: python -m harness.run_agent
  application/
    cli.py                  # только argparse и запуск runner
    runner.py               # цикл задач, волны, solutions.json, изоляция сбоев
    waves.py                # выбор задач на следующую волну и promise-модель
    script_agent.py         # ScriptAgent(BaseAgent): один ход = один bash-скрипт
    state.py                # TaskState и атомарный state.json
    prompts.py              # системный промпт, follow-up warning, вывод скрипта
    rails/                  # по одному lifecycle-rail на файл
      budget.py             # расход и лимит бюджета
      failure.py            # три ошибки модели подряд -> стоп
      followup.py           # подготовка следующей волны
      answer.py             # ответ, IMPOSSIBLE, восстановление прошлого ответа
      features.py           # признаки хода для предиктора
    features.py             # извлечение признаков и AttemptLogger
    predictor.py            # онлайн-модель вероятности успеха
    overview.py             # обзор рабочей директории
    shell.py                # запуск процессов с таймаутом и обрезкой вывода
    solutions.py            # запись solutions.json
    config.py               # Settings из CLI и окружения
    tasks.py                # чтение task.json и запись answer.txt
    llm.py                  # модели, token_cost, TokenLedger
    ojw.py                  # настройка логов openJiuwen до импорта SDK
```

Поток одного прогона:

```
cli -> runner -> tasks
             -> script_agent.invoke
                  -> Model.invoke
                  -> bash-скрипт в workspace
                  -> rails (budget / failure / followup / answer / features)
             -> waves.select -> следующий invoke
             -> solutions.record после каждого хода
```

`cli.py` не знает про волны и задачи. `script_agent.py` не выбирает, какую
задачу решать следующей. `rails/` не добавляет инструментов и не вызывает
модель; это наблюдатели lifecycle.

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
