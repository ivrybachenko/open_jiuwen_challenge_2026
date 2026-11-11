# dockerfile_checker

Проверяет Docker-образ так, как его будет запускать жюри: собирает образ,
смотрит время сборки и размер, затем прогоняет минимальный набор задач внутри
контейнера.

```bash
# значение ключа подставляет bash; Python его не читает и не печатает
export LLM_API_KEY="$NEURAL_DEEP_API_KEY"

# полная проверка: сборка + размер + прогон minimal.yaml
python -m evaluation.dockerfile_checker

# использовать уже собранный образ и записать результат в датасет
python -m evaluation.dockerfile_checker \
    --skip-build --image hack:latest --harness-version 0001 --record

# только сборка и размеры
python -m evaluation.dockerfile_checker --skip-run

# сеть жюри
python -m evaluation.dockerfile_checker --network hack-net

# локальный Docker Desktop с меньшим числом CPU
python -m evaluation.dockerfile_checker --cpus 6

# жёсткая проверка: все задачи минимального набора должны быть решены
python -m evaluation.dockerfile_checker --fail-on-unsolved
```

`LLM_BASE_URL=https://api.neuraldeep.ru/v1` оценщик передаёт контейнеру сам
через `-e`; в харнессе этого URL нет. С `--record` обязателен
`--harness-version`; каждая запись получает новый `run_id` (UUID, или
`--run-id`).

Ограничения по умолчанию соответствуют регламенту:

- размер образа — не больше 4 ГБ (`--max-image-gb`); размер берётся из
  `docker images --format "{{.Size}}"`, как у жюри, а не из `image inspect`;
- размер репозитория без `.git` — не больше 100 МБ (`--max-repo-mb`);
- таймаут сборки — 1000 секунд (`--build-timeout`);
- таймаут работы контейнера — 3600 секунд (`--run-timeout`).

Контейнер запускается с теми же ограничениями, что и у жюри: `--read-only`,
`--tmpfs /tmp`, `--cap-drop ALL`, `no-new-privileges`, 8 CPU (по умолчанию,
переопределяется `--cpus`), 16 ГБ RAM, 512 PID. Каталог задач монтируется в
`/data/tasks`, отчёты — в `/data/out`; `OUT=/data/out/solutions.json`.

После прогона задачи оцениваются тем же `answer_evaluator`, что и в остальных
чекерах, поэтому в отчёт попадают реальные баллы, токены и время. JSON
пишется в `out/reports/dockerfile_check.json`; `--keep` сохраняет временный
каталог с копией задач и `solutions.json`.

На macOS Docker Desktop может не монтировать `/var/folders/...`, поэтому по
умолчанию рабочий каталог создаётся в `<repo>/out/ojw-docker-*` (он внутри
разделяемого `/Users`). Другой каталог можно задать через `--work-dir`.

Коды возврата: `0` — все проверки прошли, `1` — сборка/размер/прогон не
прошли (или не выполнены `--min-score` / `--fail-on-unsolved`), `2` — ошибка
запуска.
