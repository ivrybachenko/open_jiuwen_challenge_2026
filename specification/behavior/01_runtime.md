# Сборка и запуск

- Состояние: реализовано
- Проверка: `docker build -t hack:latest .` и команда запуска из регламента

## Назначение

Решение собирается в Docker-образ и запускается проверяющей системой с
каталогом задач и ключом LLM-прокси.

## Сборка

`Dockerfile`:

- базовый образ `python:3.12-slim`, закреплён по digest;
- `uv` версии `0.13.7` копируется из официального образа;
- зависимости ставятся из `harness/pyproject.toml` и `harness/uv.lock`
  командой `uv sync --frozen --no-dev`;
- исходники копируются из `harness/src`, entrypoint — `/app/run_agent.py`;
- версия openJiuwen закреплена в `harness/pyproject.toml` (`0.1.19`).

## Запуск

Проверяющая система запускает контейнер с `--read-only`, записываемым
`tmpfs` в `/tmp`, `HOME=/tmp` и каталогом задач в `/data/tasks`:

```bash
docker run ... hack:latest /app/run_agent.py --tasks-dir /data/tasks
```

Контейнер не должен писать в корень файловой системы: всё изменяемое
состояние живёт в `/tmp` и в каталоге задач.

## Параметры

| Параметр | CLI | Переменная | По умолчанию |
| --- | --- | --- | --- |
| Каталог задач | `--tasks-dir` | `TASKS` | `/data/tasks` |
| Файл решений | `--out` | `OUT` | `<tasks-dir>/solutions.json` |
| Бюджет | `--budget` | `TOKEN_BUDGET`, `BUDGET`, `LLM_TOKEN_BUDGET` | без лимита |
| Модель | `--model` | `LLM_MODEL` | `qwen3.6-35b-a3b` |
| Лимит итераций | `--max-iterations` | `MAX_ITERATIONS` | `12` |
| Каталог агента | `--agent-workspace` | `AGENT_WORKSPACE` | `/tmp/agent-workspaces` |
| Число задач | `--max-tasks` | — | все задачи |
| Уровень логов | `--log-level` | — | `INFO` |

`LLM_BASE_URL` и `LLM_API_KEY` передаются только через окружение. Если `OUT`
указывает на каталог, файл решений будет `<OUT>/solutions.json`.

## Файловая система

- Корень контейнера только для чтения.
- `/tmp` — единственное место для временных файлов и артефактов агента.
- `/data/tasks` смонтирован с правом записи; туда пишутся `answer.txt` и, по
  умолчанию, `solutions.json`.
- Артефакты агента по задаче лежат в
  `/tmp/agent-workspaces/<task_id>` и очищаются перед каждым запуском задачи.

## Логи

- Сам харнесс пишет в stdout/stderr на уровне `--log-level`.
- openJiuwen переводится в console-only режим с уровнем `WARNING`, чтобы не
  писать в `./logs` на read-only файловой системе.
- Файловых логов нет. Подробнее — в
  [06_trajectories.md](06_trajectories.md).

## Известные ограничения

- Полные траектории не сохраняются.
- Параллельный запуск нескольких сессий не используется: задачи решаются
  последовательно.

## Как проверить

```bash
docker build -t hack:latest .
python -m evaluation.dockerfile_checker --harness-version 0001
```

Docker-чекер проверяет сборку, размеры образа и репозитория, а также прогоняет
минимальный набор задач в контейнере.
