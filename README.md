# OpenJiuwen Challenge 2026

Харнесс кодового агента для соревнования OpenJiuwen Challenge 2026.  
https://techarena2026.ru/open-jiuwen-challenge

## Структура проекта

```
Dockerfile                           # образ для запуска харнесса в тестовой системе
challenge_info/                      # постановка задачи, предоставленная организаторами
complexity_estimator/                # исходный код оценщика стоимости решения задачи
data/                                # датасеты для обучения и проверки моделей машинного обучения
evaluation/answer_evaluator/         # проверяет корректно ли агент решил задачу
evaluation/dockerfile_checker/       # проверяет корректность образа докер
evaluation/harness_task_checker/     # проверяет справляется ли харнесс с решением отдельных задач
evaluation/harness_task_set_checker/ # проверяет справляется ли харнесс с решением набора задач
harness/                             # исходный код харнесса
```

## Политика управления ветками Git

main - основная ветка  
harness_vXXX - тег версионирования харнесса

Харнесс версионируется инкрементально без использования SemVer. Если изменения не влияют на результат работы харнесса, то версия не меняется.  
Версия харнесса фиксируется в pyproject.toml, отмечается тегом в Git и записывается в `data/harness/harness_info.tsv`.

## Как устроено решение

Каждая задача решается отдельным `DeepAgent` из `openjiuwen.harness`:

- `SysOperationRail` даёт агенту `bash`, `read_file`, `write_file`, `edit_file`,
  `glob`, `grep`, `list_dir`;
- `cwd` агента — `workspace/` задачи (или корень задачи, если `workspace/` нет),
  артефакты агента складываются в `/tmp/agent-workspaces/<task_id>`;
- финальный ответ агент отдаёт через инструмент `write_answer`, который пишет
  `answer.txt` и в `workspace/`, и в корень задачи; после вызова инструмента
  ReAct-цикл принудительно завершается, чтобы не тратить лишний вызов модели;
- расход токенов собирает `TokenTrackingRail`; бюджет считается как
  `output + ceil(input / 10)`, рассуждения входят в output, кеш не учитывается;
- `solutions.json` перезаписывается атомарно после каждой задачи; поле `solved`
  в нём означает «ответ сдан», а корректность проверяют скрытые тесты.

Ограничения на агента: `max_iterations` (по умолчанию 12), `max_tokens=8192`
на один вызов, `restrict_to_work_dir=True`, shell-песочница `SysOperation`
(best-effort: блокирует абсолютные пути вне каталога задачи и workspace агента,
но не ловит относительный выход через `..`).

## Сборка и запуск

```bash
docker build -t hack:latest .

mkdir -p "$OUT" && chmod 777 "$OUT"

timeout -k 1000s 1h docker run --rm --name "run-${TEAM}" \
  --network hack-net \
  -e LLM_BASE_URL -e LLM_API_KEY \
  -v "$TASKS:/data/tasks:rw" \
  --read-only --tmpfs /tmp:rw,size=2g -e HOME=/tmp \
  --cap-drop ALL --security-opt no-new-privileges \
  --cpus 8 --memory 16g --pids-limit 512 \
  --workdir /app --entrypoint python \
  "hack:latest" \
  /app/run_agent.py --tasks-dir /data/tasks
```

Локальная проверка на примерах (зависимости — в локальный `harness/.venv`):

```bash
cd harness
uv sync
export LLM_BASE_URL=... LLM_API_KEY=...
cp -R ../challenge_info/task-examples /tmp/tasks
uv run python -m harness.run_agent \
  --tasks-dir /tmp/tasks --out /tmp/out/solutions.json

# unit-тесты
uv run python -m unittest discover -s test
```

Из корня репозитория то же самое:

```bash
uv run --project harness python -m harness.run_agent \
  --tasks-dir /tmp/tasks --out /tmp/out/solutions.json
```

## Переменные окружения

| Переменная | Назначение |
| --- | --- |
| `TASKS` | каталог с задачами (перекрывается `--tasks-dir`) |
| `OUT` | файл или каталог для `solutions.json`; по умолчанию `<tasks-dir>/solutions.json` |
| `LLM_BASE_URL` | адрес LLM-прокси организаторов |
| `LLM_API_KEY` | ключ прокси, в образ не попадает |
| `LLM_MODEL` | одна из четырёх моделей; по умолчанию `qwen3.6-35b-a3b` |
| `TOKEN_BUDGET` | необязательный лимит выхода в выходных токенах |
| `MAX_ITERATIONS` | лимит итераций ReAct на задачу (по умолчанию 12) |
| `AGENT_WORKSPACE` | каталог артефактов агента (по умолчанию `/tmp/agent-workspaces`) |

Те же значения можно передать флагами `--model`, `--budget`, `--max-iterations`
и `--agent-workspace`.

## Неочевидные детали

- В контейнере `--read-only` и `WORKDIR /app`. По умолчанию openJiuwen пишет
  логи в `./logs` и падает при импорте с `Read-only file system`. `ojw.py`
  переводит логгер на console-only с уровнем WARNING до первого импорта SDK.
- `openjiuwen==0.1.19` в PyPI-метаданных не ограничивает `filelock` сверху,
  хотя сам проект требует `filelock<4`. С `filelock 4.x` файловые инструменты
  падают с ошибкой `Cannot release a lock ... not held by this task`. Поэтому
  в `pyproject.toml` явно зафиксирован `filelock>=3.25.0,<4`.
- `enable_read_image_multimodal=False` отключает фоновый LLM-вызов, которым
  DeepAgent проверяет поддержку картинок; иначе он тратит бюджет впустую.
- `Runner.start()` вызывается один раз на весь прогон, `Runner.stop()` — в
  `finally`; на задачу создаётся уникальный `conversation_id`, после задачи
  сессия освобождается.
- В образ копируются `harness/src` и `harness/src/harness/run_agent.py`;
  `harness/test` и локальный `harness/.venv` в сборку не попадают.
- В образе нет `rg` и `git`: `GrepTool` работает через Python-fallback,
  worktree-инструменты не используются.
