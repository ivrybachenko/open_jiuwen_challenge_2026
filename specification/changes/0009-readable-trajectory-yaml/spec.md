# 0009. Человекочитаемая YAML-проекция траектории

- Статус: implemented
- Дата: 2026-11-10
- Заменяет (Supersedes): 0008
- Заменено (Superseded by): 0010
- Меняет поведение: `specification/behavior/06_trajectories.md`
- Связанные эксперименты: —
- Связанные обзоры литературы: —
- Затрагиваемые инварианты: `specification/constitution/01_experiment_traceability.md`

## Зачем

Канонический JSONL траекторий из 0008 хранит полный OTLP-пейлоад, но это
одна длинная JSON-строка на задачу: её тяжело читать глазами, а вложенные
prompt/message-атрибуты дублируются на каждом вызове модели. Для разбора
траектории человеком и для быстрого просмотра нужен читаемый формат.

При этом машины будут использовать траектории для обучения предсказателя
сложности, поэтому нельзя терять точные данные. Решение — два артефакта:
JSONL остаётся источником истины, YAML становится читаемой проекцией.

## Что меняется

- В каталоге траекторий сохраняется прежний
  `trajectories_default.jsonl` (полный OTLP, источник истины для обучения).
- Дополнительно на каждую задачу пишется
  `<trajectories-dir>/readable/<task_id>__<trajectory_id>.yaml`.
- YAML содержит:
  - `task_id`, `trajectory_id`, модель, время начала и длительность;
  - текст задачи (первое пользовательское сообщение);
  - шаги в хронологическом порядке:
    - `kind: llm`: `reasoning` (блок многострочного текста), `content`,
      `tool_calls`, `usage`, время и длительность;
    - `kind: tool`: `tool`, `arguments`, `result`, `error`, время и
      длительность.
- В YAML не дублируются полные prompt-истории и event-span'ы: они остаются
  в JSONL. YAML — обзор решения, а не второй источник истины.
- Если YAML не удалось построить, JSONL всё равно сохраняется, в лог пишется
  предупреждение, решение задачи не прерывается.
- Формат YAML — обычный словарь; машины читают его `yaml.safe_load` или
  предпочитают JSONL, если нужна побитовая точность OTLP.

## Критерии приёмки

- [x] AC-1: после задачи с включённым каталогом траекторий существуют и
  `trajectories_default.jsonl`, и один файл `readable/*.yaml`.
- [x] AC-2: YAML-файл читается `yaml.safe_load` и содержит `task_id`, список
  `steps`, минимум один шаг `llm` с `reasoning` (если модель вернула
  рассуждения) и минимум один шаг `tool` с именем и результатом.
- [x] AC-3: JSONL по-прежнему содержит полный OTLP-пейлоад, включая
  `reasoning_content`; YAML не заменяет его.
- [x] AC-4: ошибка построения YAML не удаляет JSONL и не прерывает задачу.
- [x] AC-5: `README.md`, `evaluation/README.md`,
  `specification/behavior/06_trajectories.md` и
  `data/trajectories/README.md` описывают оба формата и их назначение.

## Вне рамок

- Замена JSONL на YAML в качестве единственного формата.
- Загрузка YAML обратно в `Trajectory`.
- Автоматическое удаление YAML при ротации JSONL.
- Обучение предсказателя сложности.

## Ограничения

- YAML пишется через PyYAML; добавляется явная зависимость `pyyaml`.
- YAML — проекция без полных prompt-историй и event-span'ов, поэтому для
  точного обучения нужно читать JSONL.
- Размер YAML растёт вместе с траекторией; файлы в git не хранятся.

## Проверка

Результаты на 2026-11-10:

- AC-1, AC-2, AC-3: реальный прогон
  `LLM_API_KEY=... python3 -m evaluation.harness_task_checker --task math/solvable/0001`
  завершился `SOLVED`. Появились `data/trajectories/trajectories_default.jsonl`
  и `data/trajectories/readable/math_0000__f529e028-….yaml`. YAML прочитан
  `yaml.safe_load`: 6 шагов `[llm, tool, llm, tool, llm, tool]`, у первого
  LLM-шага 452 символа `reasoning`, tool-шаги `bash`, `bash`, `write_answer`;
  JSONL содержит `reasoning_content`.
- AC-4: `cd harness && .venv/bin/python -m unittest test.test_trajectory` —
  тест подменяет проекцию на исключение и проверяет, что JSONL создан, а
  исключение не выходит наружу.
- AC-5: документы обновлены; в YAML-примере и README указано, что JSONL —
  источник истины, а YAML — читаемая проекция.
- Полный набор: `cd harness && .venv/bin/python -m unittest discover -s test`
  — 9 тестов OK; `python3 -m unittest discover -s evaluation/test -t .` — 68
  тестов OK.

## Риски и откат

- Риск: YAML окажется неудобным для больших tool-output. Откат — удалить
  `readable/` и продолжать читать JSONL; код записи можно отключить.
- Риск: YAML-сериализация падает на нестандартном объекте. Митигация —
  исключение перехватывается, JSONL уже записан.
