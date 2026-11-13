# harness

Исходники харнесса. Точка входа — `src/harness/run_agent.py`; `main` живёт
там, а `cli.py` только разбирает аргументы.

## Слои

```
src/harness/
  run_agent.py                  # entrypoint: main + logging
  cli.py                        # только argparse
  config.py                     # Settings, список моделей

  domain/                       # чистые данные и правила
    tasks.py                    # Task, answer.txt
    state.py                    # TaskState
    attempts.py                 # AnswerInfo, classify_answer, extract_features
    budget.py                   # token_cost, TokenLedger

  application/                  # сценарии: что и в каком порядке делать
    runner.py                   # цикл задач, волны, solutions.json
    waves.py                    # выбор следующей волны и expected value

  agents/                       # как выполняется один ход
    script_agent.py             # ScriptAgent(BaseAgent), SYSTEM_PROMPT
    rails/
      budget.py
      failure.py
      followup.py               # follow-up warning
      answer.py
      features.py

  success_predictors/           # оценка вероятности успеха
    heuristic.py                # success_probability
    model.py                    # онлайн-модель; данные в models/
    __init__.py                 # estimate_success: модель -> эвристика

  infrastructure/               # адаптеры к ОС, диску и логам
    attempt_log.py              # AttemptLogger (JSONL + YAML)
    logging_setup.py            # настройка логов openJiuwen до импорта SDK
    overview.py                 # обзор рабочей директории
    shell.py                    # процессы с таймаутом и обрезкой вывода
    solutions.py                # solutions.json
    state_store.py              # атомарный state.json
    tasks.py                    # чтение task.json
```

Поток одного прогона:

```
cli -> application.runner
          -> agents.script_agent.invoke
               -> Model.invoke
               -> bash-скрипт в workspace
               -> agents.rails (budget / failure / followup / answer / features)
          -> application.waves.select
          -> infrastructure.solutions.record после каждого хода
```

Принцип разделения:

- `domain/` не знает про файлы и openJiuwen;
- `application/` решает, что запускать дальше;
- `agents/` выполняет один ход и содержит только его промпты;
- `success_predictors/` изолирует две стратегии оценки вероятности;
- `infrastructure/` реализует I/O: процессы, файлы, логи, JSON-хранилища;
- `cli.py` и `run_agent.py` — интерфейс, без бизнес-логики.

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
