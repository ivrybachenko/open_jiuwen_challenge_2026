# OpenJiuwen Challenge 2026

Харнесс кодового агента для соревнования OpenJiuwen Challenge 2026.



## Структура проекта

```
Dockerfile            # образ харнесса
pyproject.toml        # зависимости проекта
uv.lock               # зафиксированное дерево зависимостей
challenge_info/       # постановка задачи, предоставленная организаторами
src/
  run_agent.py        # точка входа
  harness/            # исходный код харнесса
```

Зависимости управляются через `uv`: `pyproject.toml` + `uv.lock`, установка
идёт в `/app/.venv` (не глобально). Всё содержимое `src/` копируется в образ
в `/app`, поэтому жюри запускает `python /app/run_agent.py --tasks-dir /data/tasks`,
а `python` в PATH указывает на `venv`.

Текущее состояние — минимальный каркас: инфраструктура запуска, учёта токенов
и сохранения результатов готова, стратегия решения (`solver.py`) пока заглушка.

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

Локальная проверка на примерах (зависимости — в локальный `.venv`):

```bash
uv sync
cp -R challenge_info/task-examples /tmp/tasks
uv run python src/run_agent.py --tasks-dir /tmp/tasks --out /tmp/out/solutions.json
```

## Переменные окружения

| Переменная | Назначение |
| --- | --- |
| `TASKS` | каталог с задачами (перекрывается `--tasks-dir`) |
| `OUT` | файл или каталог для `solutions.json`; по умолчанию `<tasks-dir>/solutions.json` |
| `LLM_BASE_URL` | адрес LLM-прокси организаторов |
| `LLM_API_KEY` | ключ прокси, в образ не попадает |
