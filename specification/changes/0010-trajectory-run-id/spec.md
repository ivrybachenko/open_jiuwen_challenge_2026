# 0010. Связь траектории с датасетом через run_id

- Статус: implemented
- Дата: 2026-11-10
- Заменяет (Supersedes): 0009
- Заменено (Superseded by): —
- Меняет поведение: `specification/behavior/06_trajectories.md`
- Связанные эксперименты: —
- Связанные обзоры литературы: —
- Затрагиваемые инварианты: `specification/constitution/01_experiment_traceability.md`

## Зачем

Датасеты `data/harness_task_score/` и `data/harness_task_set_score/`
идентифицируют строку через `run_id`. Траектория сейчас знает только
`task_id`, поэтому одну из нескольких попыток решения одной задачи нельзя
однозначно сопоставить со строкой датасета: `task_id` повторяется при каждом
повторе.

Нужна сквозная связь: тот же `run_id`, что записан в датасет, должен быть в
траектории и в YAML-проекции.

## Что меняется

- У харнесса появляется параметр `--run-id` (переменная окружения
  `HARNESS_RUN_ID`). Значение непрозрачное: харнесс его не генерирует, а
  только сохраняет.
- Оценщики передают в харнесс тот же `run_id`, который потом пишут в датасет:
  - `harness_task_checker` — `--run-id` из своего аргумента или новый UUID;
  - `harness_task_set_checker` — аналогично;
  - `commit_harness_version` — `run_id`, сгенерированный для конкретной
    записи.
- В JSONL ресурсный атрибут `harness.run_id` содержит переданное значение.
- В YAML появляется поле `run_id` рядом с `task_id` и `trajectory_id`.
- Если `--run-id` не передан, поведение прежнее: поле не добавляется, связь
  остаётся по `task_id`.
- Значение `run_id` не влияет на решение задачи, бюджет и порядок задач.

## Критерии приёмки

- [x] AC-1: `harness_task_checker --record` передаёт в харнесс тот же
  `run_id`, который записывается в `data/harness_task_score/*.tsv`.
- [x] AC-2: при заданном `--run-id` JSONL-запись содержит ресурсный атрибут
  `harness.run_id` с этим значением, а YAML — поле `run_id`.
- [x] AC-3: без `--run-id` траектория и YAML не содержат `run_id`, прогон
  работает как раньше.
- [x] AC-4: `harness_task_set_checker` и `commit_harness_version` используют
  тот же `run_id`, что и соответствующая запись датасета.
- [x] AC-5: README, `evaluation/README.md`,
  `specification/behavior/06_trajectories.md` и
  `data/trajectories/README.md` описывают join по `run_id`.

## Вне рамок

- Генерация `run_id` внутри харнесса.
- Изменение схемы TSV-датасетов.
- Гарантия, что каждый запуск с `--record` использует уникальный `run_id`:
  это уже проверяет `record_*_score`.
- Связывание траекторий с `task_set_score` по отдельным задачам: у набора
  одна строка на весь прогон, задачи остаются видны по `task_id`.

## Ограничения

- `run_id` уникален в пределах одного датасета; `task_score` и
  `task_set_score` используют независимые пространства.
- При прогоне без `--record` `run_id` известен только из вывода чекера, и
  строки в датасете может не быть.
- Docker-прогон `dockerfile_checker` траектории не сохраняет; связывать нечего.

## Проверка

Результаты на 2026-11-10:

- AC-1, AC-4: `python3 -m unittest evaluation.test.test_commit_harness_version`
  — тест подменяет `check_task`, падающий прогон всё равно записывает строку
  датасета, и её `run_id` совпадает с `config.run_id`, переданным в харнесс.
  `python3 -m unittest evaluation.test.test_runner` проверяет, что
  `HarnessConfig.run_id` добавляет `--run-id` в команду харнесса.
- AC-2, AC-3: `harness/test/test_trajectory.py` проверяет отсутствие поля без
  `run_id` и наличие `harness.run_id`/`run_id` с ним. Реальный прогон
  `python3 -m evaluation.harness_task_checker --task math/solvable/0002 --run-id verify-run-001`
  завершился `SOLVED`; в JSONL `Trajectory.resource_attributes["harness.run_id"]`
  равен `verify-run-001`, в YAML поле `run_id` тоже `verify-run-001`.
- AC-5: документы обновлены.
- Полный набор: `cd harness && .venv/bin/python -m unittest discover -s test`
  — 12 тестов OK; `python3 -m unittest discover -s evaluation/test -t .` — 70
  тестов OK.

## Риски и откат

- Риск: чекер передаст `run_id` одной записи, а запишет другую. Митигация —
  в `commit_harness_version` `run_id` создаётся до запуска и передаётся в
  оба места.
- Риск: `run_id` попадёт в клиентский контекст модели. Нет: это ресурсный
  атрибут траектории, в prompt он не добавляется.
