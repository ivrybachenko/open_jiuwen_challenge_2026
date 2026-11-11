# Логи и траектории

- Состояние: реализовано
- Читатель: разработчик и coding-агент; организатор читает `README.md`
- Проверки: [таблица проверок](#как-проверить)

## Что сохраняется сейчас

- **Логи харнесса.** Пишутся в stdout/stderr на уровне `--log-level`
  (по умолчанию `INFO`): загрузка задач, результат по каждой задаче
  (`solved`, `reward`, `cost`, `spent`, `total`), итог прогона.
- **Логи openJiuwen.** Переведены в console-only режим с уровнем `WARNING`;
  файловых логов нет.
- **`solutions.json`.** В поле `note` по каждой задаче фиксируются
  `result_type`, признак получения ответа через `write_answer` или из
  `answer.txt`, текст ошибки, если задача упала.
- **Отчёты оценщика.** В `out/reports/*.json` сохраняются команда запуска,
  код возврата, таймаут, длительность, хвосты stdout/stderr (последние 4000
  символов) и результат по каждой задаче.
- **Артефакты агента.** Каталог `/tmp/agent-workspaces/<task_id>` существует
  во время прогона; в контейнере он исчезает вместе с контейнером. Локально
  его можно сохранить.

## Полные траектории

Траектории включаются флагом `--trajectories-dir` или переменной окружения
`TRAJECTORIES_DIR`. Без них харнесс не включает запись и не создаёт каталог.
Зачётный запуск по регламенту флаг не передаёт.

При заданном каталоге харнесс:

1. включает observability встроенными средствами openJiuwen
   (`acquire_observability`);
2. добавляет к агенту встроенный `TrajectoryRail` с общим
   `TrajectorySpanProcessor` и `FileTrajectoryStore`;
3. открывает на каждую задачу корневой span, без которого SDK не создаёт
   LLM/tool-span'ы;
4. после задачи сохраняет одну каноническую траекторию в
   `<trajectories-dir>/trajectories_default.jsonl` и читаемую проекцию в
   `<trajectories-dir>/readable/<task_id>__<trajectory_id>.yaml`.

JSONL — источник истины для обучения: в нём полные prompt-истории,
event-span'ы и все OTLP-атрибуты. YAML — обзор для человека: шаги `llm`
(рассуждения, ответ, вызовы инструментов, расход) и `tool` (имя, аргументы,
результат, ошибка), текст задачи и тайминги. Полные prompt-истории и
служебные event-span'ы в YAML не дублируются.

Если YAML не удалось построить, JSONL уже записан, в лог пишется
предупреждение, задача продолжается.

Что попадает в запись:

- LLM-span'ы: входные сообщения, ответ, рассуждения модели
  (`reasoning_content`, часть `"type": "reasoning"`), определения
  инструментов и расход токенов;
- tool-span'ы: имя инструмента, аргументы, результат и ошибка;
- event-span'ы контекста, которые openJiuwen относит к той же траектории.

Ресурсные атрибуты содержат `gen_ai.conversation.id` (в API траектории —
`Trajectory.session_id`), равный `task_id` из `task.json`. Это то же значение,
под которым задача записана в `solutions.json`; датасетный путь
(`coding/solvable/0001`) соединяется с траекторией через `task.json` или отчёт
оценщика.

Оценщики (`harness_task_checker`, `harness_task_set_checker`,
`commit_harness_version`) передают `--trajectories-dir <repo>/data/trajectories`
автоматически. Они же передают `--run-id`: тот же UUID, который пишется в
`data/harness_task_score/` или `data/harness_task_set_score/`. Поэтому
траекторию можно соединить со строкой датасета по `run_id`, не угадывая
попытку по `task_id`. В JSONL это ресурсный атрибут `harness.run_id`, в YAML —
поле `run_id`. Сырые OTLP-файлы observability пишутся во временный каталог и
не являются источником данных.

Если observability не удалось инициализировать, в лог пишется
`trajectory capture disabled`, и прогон продолжается без траекторий.

## Ограничения

- Формат траектории принадлежит openJiuwen (`0.1.19`) и меняется вместе с
  SDK.
- Если провайдер не возвращает `reasoning_content`, рассуждений в записи не
  будет.
- Файл `trajectories_default.jsonl` дописывается и не ротируется; в git он не
  хранится.
- YAML — проекция, а не второй источник истины: для точного обучения читайте
  JSONL. YAML-файлы тоже не хранятся в git.
- `--log-level DEBUG` повышает детализацию логов харнесса, но openJiuwen
  остаётся на `WARNING`.

## Как проверить

Общие команды и флаги — в [`evaluation/README.md`](../../evaluation/README.md).
Все команды запускаются из корня репозитория.

| ID | Уровень | Что подтверждает | Проверка | Ожидаемо |
| --- | --- | --- | --- | --- |
| V-1 | интеграционная | логи и отчёт сохраняются | `python -m evaluation.harness_task_set_checker --task-set data/task_set/example.yaml --keep` | в отчёте есть `harness.stdout_tail` и `harness.stderr_tail`; временный каталог сохранён |
| V-2 | интеграционная | траектория с инструментами и рассуждениями сохраняется | `python -m evaluation.harness_task_checker --task math/solvable/0001 --keep` | в `data/trajectories/trajectories_default.jsonl` появилась запись; в `data/trajectories/readable/` появился YAML с шагами `llm` и `tool`, рассуждениями и результатом инструмента |
| V-3 | быстрая | без флага траектории не включаются | `cd harness && uv run python -m unittest test.test_config` | `Settings.trajectories_dir is None` |
| V-4 | быстрая | YAML и JSONL пишутся вместе, ошибка YAML не теряет JSONL | `cd harness && uv run python -m unittest test.test_trajectory` | оба файла создаются; при ошибке YAML JSONL остаётся |
| V-5 | интеграционная | `run_id` связывает траекторию с датасетом | `python -m evaluation.harness_task_checker --task math/solvable/0001 --run-id check-1` | в JSONL есть `harness.run_id=check-1`, в YAML — `run_id: check-1` |

`--keep` сохраняет временный каталог прогона, чтобы разобрать артефакты.
