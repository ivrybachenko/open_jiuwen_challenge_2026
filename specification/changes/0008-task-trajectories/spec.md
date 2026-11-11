# 0008. Траектории задач для предсказателя сложности

- Статус: implemented
- Дата: 2026-11-10
- Заменяет (Supersedes): —
- Заменено (Superseded by): 0009
- Меняет поведение: `specification/behavior/06_trajectories.md`,
  `specification/behavior/01_runtime.md`, `specification/behavior/03_solver.md`
- Связанные эксперименты: —
- Связанные обзоры литературы: —
- Затрагиваемые инварианты: `specification/constitution/01_experiment_traceability.md`

## Зачем

Для обучения предсказателя сложности задачи нужны данные о том, как агент
решает задачу: какие инструменты он вызывал, что они вернули и как модель
рассуждала перед действиями. Сейчас сохраняются только итоговый ответ,
стоимость и краткая пометка в `solutions.json`; полной траектории нет.

Данные нужны при тестовых прогонах харнесса на задачах, а не в зачётном
контейнере. Поэтому сохранение включается каталогом траекторий и по умолчанию
пишет в `data/trajectories/`.

## Что меняется

- У харнесса появляется параметр `--trajectories-dir` (переменная окружения
  `TRAJECTORIES_DIR`). Без него траектории не пишутся.
- Если каталог задан, харнесс включает observability встроенными средствами
  openJiuwen и сохраняет по одной канонической траектории на задачу в
  `<trajectories-dir>/trajectories_default.jsonl` (JSONL, OTLP-представление).
- В траектории остаются:
  - вызовы инструментов: имя, аргументы, результат и ошибка, если была;
  - обмен с моделью: входные сообщения, ответ, рассуждения модели
    (`reasoning_content`) и определения инструментов;
  - служебные события контекста, которые openJiuwen относит к той же
    траектории.
- Запись привязана к `session_id` задачи, поэтому траектории из одного файла
  можно сопоставить с `task_id` и результатами в `solutions.json` /
  `data/harness_task_score/`.
- Оценщики харнесса (`harness_task_checker`, `harness_task_set_checker`,
  `commit_harness_version`) передают `--trajectories-dir` в
  `data/trajectories/` по умолчанию. Зачётный запуск по регламенту траектории
  не сохраняет.
- Если observability не удалось инициализировать, харнесс пишет предупреждение
  и продолжает решать задачи без траекторий: сбор данных не должен ломать
  прогон.

## Критерии приёмки

- [x] AC-1: без `--trajectories-dir` и `TRAJECTORIES_DIR` каталог траекторий
  не создаётся и файл траекторий не появляется.
- [x] AC-2: при заданном каталоге после решения задачи существует
  `<trajectories-dir>/trajectories_default.jsonl`, в нём есть запись с
  `gen_ai.conversation.id` (в API — `session_id`), равным `task_id` из
  `task.json`, и в записи присутствуют минимум один инструментальный span и
  один LLM-span с сообщениями.
- [x] AC-3: рассуждения модели попадают в траекторию: в LLM-span есть
  сообщение с частью типа `reasoning`, если провайдер вернул
  `reasoning_content`.
- [x] AC-4: `python -m evaluation.harness_task_checker --task ...` передаёт
  харнессу `--trajectories-dir <repo>/data/trajectories`.
- [x] AC-5: ошибка инициализации траекторий не отменяет решение задачи:
  результат задачи и `solutions.json` сохраняются как раньше.
- [x] AC-6: текущее поведение и README организатора описывают новый режим и
  не обещают траектории в зачётном контейнере.

## Вне рамок

- Обучение предсказателя сложности и извлечение признаков из траектории.
- Оценка сложности задачи до решения и выбор задач по сложности.
- Сохранение траекторий в Docker-образе или в зачётном контейнере.
- Сжатие, ротация и очистка файла траекторий.
- Собственный формат траектории: используется встроенный формат openJiuwen.

## Ограничения

- Контейнер запускается с `--read-only`, поэтому писать траектории можно только
  в смонтированный каталог или в `/tmp`. Зачётный запуск не задаёт
  `--trajectories-dir` и ничего не пишет.
- Observability добавляет накладные расходы на сериализацию сообщений, поэтому
  режим включается только для сбора данных.
- Формат и доступность полей зависят от версии openJiuwen (`0.1.19`).
- Для observability добавляется зависимость
  `opentelemetry-exporter-otlp-proto-common`: без неё встроенный обработчик
  span'ов openJiuwen не импортируется.
- Если провайдер не возвращает `reasoning_content`, рассуждений в траектории
  не будет; это ограничение модели, а не харнесса.

## Проверка

Результаты на 2026-11-10:

- AC-1: `cd harness && .venv/bin/python -m unittest discover -s test` — 7
  тестов, включая `test_config.TrajectoriesDirTest`; без флага и переменной
  `Settings.trajectories_dir is None`.
- AC-2, AC-3: реальный прогон
  `LLM_API_KEY=... python3 -m evaluation.harness_task_checker --task math/solvable/0001`
  завершился `SOLVED`. В `data/trajectories/trajectories_default.jsonl`
  появилась 1 запись, `Trajectory.session_id = math_0000`; разбор встроенными
  функциями дал 3 LLM-span, 3 tool-span и 3 сообщения с `reasoning_content`
  (`iter_spans`, `read_llm_exchange`, `read_tool_call`, `span_category`).
- AC-4: `python3 -m unittest evaluation.test.test_runner` — 4 теста, включая
  проверку `--trajectories-dir <repo>/data/trajectories` и отключение флага.
  Полный набор: `python3 -m unittest discover -s evaluation/test -t .` — 68
  тестов, OK.
- AC-5: запуск `TrajectoryRecorder('/dev/null/not-a-dir').start()` пишет
  `trajectory capture disabled`, `enabled` остаётся `False`, исключение не
  выходит наружу.
- AC-6: обновлены `README.md`, `evaluation/README.md`,
  `specification/behavior/01_runtime.md`, `03_solver.md`, `06_trajectories.md`,
  `specification/behavior/README.md`, `data/trajectories/README.md`.

## Риски и откат

- Риск: файл траекторий быстро растёт. Откат — не передавать
  `--trajectories-dir` или очистить `data/trajectories/`.
- Риск: ошибка SDK ломает прогон. Митигация — инициализация обёрнута в
  try/except, предупреждение в лог, решение продолжается.
- Риск: в траекторию попадают лишние данные. Формат и набор span'ов
  контролируются встроенным `TrajectoryRail`; при необходимости каталог
  удаляется, на решение это не влияет.
