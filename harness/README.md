# harness

Исходники харнесса. Точка входа — `src/harness/run_agent.py`; `main` живёт
там, а `cli.py` только разбирает аргументы.

## Слои

```
src/harness/
  run_agent.py                  # entrypoint: main + logging + python -m harness.run_agent
  cli.py                        # только argparse
  config.py                     # Settings из CLI и окружения
  application/                  # сценарии: что и в каком порядке делать
    runner.py                   # цикл задач, волны, solutions.json
    waves.py                    # выбор следующей волны и promise-модель
    script_agent.py             # ScriptAgent(BaseAgent), SYSTEM_PROMPT, один ход
    state.py                    # TaskState и state.json
    rails/
      budget.py                 # расход и лимит бюджета
      failure.py                # три ошибки модели подряд -> стоп
      followup.py               # follow-up warning и подготовка волны
      answer.py                 # ответ, IMPOSSIBLE, восстановление ответа
      features.py               # признаки хода для предиктора
  infrastructure/               # адаптеры: процессы, файлы, модели, логи
    attempts.py                 # признаки попытки и AttemptLogger
    llm.py                      # модели, token_cost, TokenLedger
    logging_setup.py            # настройка логов openJiuwen до импорта SDK
    overview.py                 # обзор рабочей директории
    predictor.py                # онлайн-модель вероятности успеха
    shell.py                    # процессы с таймаутом и обрезкой вывода
    solutions.py                # запись solutions.json
    tasks.py                    # чтение task.json и запись answer.txt
```

Поток одного прогона:

```
cli -> application.runner
          -> application.script_agent.invoke
               -> Model.invoke
               -> bash-скрипт в workspace
               -> application.rails (budget / failure / followup / answer / features)
          -> application.waves.select -> следующий invoke
          -> infrastructure.solutions.record после каждого хода
```

Границы:

- `cli.py` не знает про задачи и волны.
- `application/` решает, что запускать и как выполнять один ход.
- `application/rails/` не выбирает задачи и не вызывает модель; это
  наблюдатели lifecycle.
- `infrastructure/` не импортирует `application/`.
- Промпты лежат там, где используются: `SYSTEM_PROMPT` — в
  `application/script_agent.py`, follow-up warning — в
  `application/rails/followup.py`.

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
