# harness

Исходники харнесса. Точка входа — `src/harness/run_agent.py`; `main` живёт
там, а `infrastructure/cli.py` только разбирает аргументы.

## Структура

```
src/harness/
  run_agent.py                  # entrypoint: main + logging
  config.py                     # Settings, список моделей

  infrastructure/               # оболочка процесса
    cli.py                      # только argparse
    logging_setup.py            # логи openJiuwen до импорта SDK

  tasks/                        # что решаем
    model.py                    # Task, answer.txt
    loader.py                   # чтение task.json
    state.py                    # TaskState
    store.py                    # state.json
    answer.py                   # AnswerInfo, classify_answer

  solving/                      # как получаем ответ
    runner.py                   # цикл задач и волны
    waves.py                    # выбор следующей волны
    agents/
      script_agent.py           # ScriptAgent(BaseAgent), SYSTEM_PROMPT
      rails/
        budget.py
        failure.py
        followup.py             # follow-up warning
        answer.py
        features.py
    workspace/
      overview.py               # обзор каталога
      shell.py                  # процессы с таймаутом и обрезкой вывода
    success_predictors/
      heuristic.py              # success_probability
      model.py                  # predict_success
      models/                   # артефакты sklearn
      __init__.py               # estimate_success: модель -> эвристика

  accounting/                   # что тратим и записываем
    budget.py                   # token_cost, TokenLedger
    attempts.py                 # признаки хода + AttemptLogger
    solutions.py                # solutions.json
```

Три домена:

- `tasks/` — что решаем, что помним и что считается ответом;
- `solving/` — как получаем ответ: runner, волны, агент, rails, workspace и
  предсказание успеха;
- `accounting/` — что тратим и записываем: бюджет, журнал попыток,
  `solutions.json`.

`infrastructure/` — только процессная оболочка: разбор аргументов и настройка
логов openJiuwen. Бизнес-логики там нет.

Поток одного прогона:

```
infrastructure.cli -> solving.runner
                         -> solving.agents.script_agent.invoke
                              -> Model.invoke
                              -> bash-скрипт в workspace
                              -> solving.agents.rails
                         -> solving.waves.select
                         -> accounting.solutions.record после каждого хода
```

Промпты лежат рядом с использованием: `SYSTEM_PROMPT` — в
`solving/agents/script_agent.py`, follow-up warning — в
`solving/agents/rails/followup.py`.

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
