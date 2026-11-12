# Логи и траектории

- Состояние: реализовано
- Читатель: разработчик и coding-агент; организатор читает `README.md`
- Проверки: [таблица проверок](#как-проверить)

## Что сохраняется сейчас

- **Логи харнесса.** Пишутся в stdout/stderr на уровне `--log-level`
  (по умолчанию `INFO`): загрузка задач, границы волн, результат по каждой
  задаче (`kind`, `solved`, `reward`, `cost`, `spent`, `total`), итог прогона.
- **Логи openJiuwen.** Переведены в console-only режим с уровнем `WARNING`;
  файловых логов нет.
- **`solutions.json`.** После каждого хода фиксируются вид ответа, число
  ходов, ошибка модели или скрипта, накопленные токены и стоимость.
- **Отчёты оценщика.** В `out/reports/*.json` сохраняются команда запуска,
  код возврата, таймаут, длительность, хвосты stdout/stderr и результат по
  каждой задаче.
- **Состояние задачи.** `<agent-workspace>/<task_id>/state.json` хранит обзор,
  историю сообщений, ходы, признаки и лучший ответ. В контейнере исчезает
  вместе с ним.
- **Скрипты агента.** `<agent-workspace>/<task_id>/turn_NN.sh`; рабочая копия
  `.harness_step_NN.sh` удаляется после исполнения.

## Журнал попыток

Траектории включаются флагом `--trajectories-dir` или переменной окружения
`TRAJECTORIES_DIR`. Без них харнесс не пишет журнал. Зачётный запуск по
регламенту флаг не передаёт.

При заданном каталоге после каждого хода харнесс пишет:

| Файл | Для кого | Что внутри |
| --- | --- | --- |
| `<dir>/bash_attempts.jsonl` | машины | Одна JSON-строка на ход: задача, волна, обзор, рассуждение, ответ модели, скрипт, вывод, код возврата, расход и признаки. Источник истины. |
| `<dir>/readable/<task_id>__waveN__<time>.yaml` | человек | Читаемая проекция той же записи с многострочными блоками. |

JSONL дописывается и не ротируется. YAML — удобный просмотр, а не второй
источник истины: если YAML не удалось записать, JSONL остаётся.

Поля JSONL:

- `task_id`, `task_type`, `task_path`, `task_root`, `model`;
- `wave`, `turn`, `started_at`, `duration_seconds`;
- `overview` и `reasoning` — что видела модель и что она думала;
- `content`, `script`, `output`, `exit_code`, `timed_out`, `script_error`;
- `answer`, `answer_kind`, `input_tokens`, `output_tokens`,
  `reasoning_tokens`, `finish_reason`, `model_error`;
- `features` — длина рассуждения, ключевые слова, обрыв по лимиту, форма
  скрипта, результат исполнения, вид ответа;
- `run_id`, `logged_at`.

`task_id` — то же значение, под которым задача лежит в `solutions.json`.
Оценщики передают `--run-id`; тот же UUID попадает в JSONL и в строку
`data/harness_task_score/` или `data/harness_task_set_score/`.

## Старые траектории

`trajectories_default.jsonl` и `readable/*.yaml` от `harness_v0001` остаются в
`data/trajectories/` как история. `harness_v0002` их не пишет: у bash-солвера
нет инструментальных вызовов openJiuwen, а журнал попыток содержит всё, что
нужно для обучения предсказателя.

## Ограничения

- Формат журнала принадлежит харнессу, а не openJiuwen; он меняется вместе с
  `features.py`.
- Если провайдер не возвращает `reasoning_content`, рассуждений в записи не
  будет.
- `bash_attempts.jsonl` дописывается и не ротируется; в git он не хранится.
- `--log-level DEBUG` повышает детализацию логов харнесса, но openJiuwen
  остаётся на `WARNING`.

## Как проверить

Общие команды и флаги — в [`evaluation/README.md`](../../evaluation/README.md).
Все команды запускаются из корня репозитория, кроме harness-тестов.

| ID | Уровень | Что подтверждает | Проверка | Ожидаемо |
| --- | --- | --- | --- | --- |
| V-1 | быстрая | журнал попыток пишется вместе с YAML | `cd harness && uv run python -m unittest test.test_features` | JSONL и YAML создаются |
| V-2 | интеграционная | после задачи появилась запись с признаками | `python -m evaluation.harness_task_checker --task math/solvable/0001 --run-id check-1` | в `bash_attempts.jsonl` есть `run_id=check-1`, волна, скрипт, вывод и `features` |
| V-3 | быстрая | без флага журнал не включается | `cd harness && uv run python -m unittest test.test_config` | `Settings.trajectories_dir is None` |
