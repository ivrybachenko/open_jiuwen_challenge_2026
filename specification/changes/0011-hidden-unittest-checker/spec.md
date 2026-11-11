# 0011. Проверка `hidden_unittest` для задач с закрытыми тестами

- Статус: implemented
- Дата: 2026-11-10
- Заменяет (Supersedes): —
- Заменено (Superseded by): —
- Меняет поведение: `specification/behavior/07_evaluation.md`
- Связанные эксперименты: —
- Связанные обзоры литературы: `research/literature_review/0004-dataset-difficulty-and-unsolvable/`
- Затрагиваемые инварианты: `specification/constitution/06_task_authoring.md`

## Зачем

Тренировочный набор расширяется задачами, где проверяющий код не должен быть
виден агенту: алгоритмические задачи с наборами входов и задач, где ответ
сверяется с эталонной программой. Проверка `unittest` запускает только
`test*.py` из рабочего каталога, поэтому такие задачи нельзя использовать:
агент видит тесты и может подогнать ответ под них.

Нужен отдельный тип проверки, который запускает тесты из служебного каталога
задачи, недоступного как рабочий каталог агента.

## Что меняется

- `answer_evaluator` понимает `check: "hidden_unittest"`.
- Тесты берутся из `<task-dir>/tests/**/test*.py`, а не из `workspace/`.
- Тесты запускаются с рабочим каталогом `workspace/` и с `workspace/` в
  `PYTHONPATH`, чтобы проверяемый код импортировался как модуль задачи.
- Как и для `unittest`, нужен непустой `answer.txt`: одних прошедших тестов
  недостаточно.
- `harness_task_checker` и `harness_task_set_checker` хешируют файлы
  `tests/**/test*.py` перед прогоном и отвергают результат, если агент изменил,
  удалил или добавил тест.
- `--allow-test-edits` отключает эту защиту так же, как для `unittest`.
- Неизвестный `check` по-прежнему даёт 0 баллов.
- Задачи с `hidden_unittest` не попадают в рабочий каталог агента: каталог
  `tests/` лежит рядом с `workspace/`, а не внутри него.

## Критерии приёмки

- [x] AC-1: `evaluate_task` с `check="hidden_unittest"` возвращает `solved=true`,
  когда тесты из `tests/` проходят и `answer.txt` непустой, и `solved=false`,
  когда тесты падают, `answer.txt` пуст или каталога `tests/` нет.
- [x] AC-2: тесты `hidden_unittest` не находятся в `workspace/` и не находятся
  поиском `iter_test_files(workspace)`.
- [x] AC-3: `harness_task_set_checker` обнаруживает изменение файла в `tests/`
  и не засчитывает задачу; `--allow-test-edits` отключает проверку.
- [x] AC-4: `python -m unittest discover -s evaluation/test -t .` проходит,
  включая новые тесты проверки.
- [x] AC-5: `evaluation/README.md`, `evaluation/answer_evaluator/README.md` и
  `specification/behavior/07_evaluation.md` описывают новый тип проверки.

## Вне рамок

- Изменение харнесса и его песочницы: агент по-прежнему получает только
  `workspace/`, но абсолютная изоляция от `..` не гарантируется.
- Шифрование или сокрытие тестов от файловой системы.
- Новые типы проверок, кроме `hidden_unittest`.

## Ограничения

- Тесты должны быть обычными Python-файлами без сторонних зависимостей.
- Проверяющий код живёт в репозитории, поэтому это защита от подгонки под
  видимые тесты, а не от чтения файлов через `..`.
- Формат `task.json` не меняется.

## Проверка

Результаты на 2026-11-11:

- AC-1, AC-2: `evaluation/test/test_answer_evaluator.py`, класс
  `HiddenUnittestCheckTest` — 5 тестов: успех, падение, отсутствие тестов,
  обязательный `answer.txt`, отсутствие скрытых тестов в
  `iter_test_files(workspace)`.
- AC-3: `evaluation/test/test_suite.py`, тест
  `test_hidden_test_edits_invalidate_task` — изменение `tests/test_hidden.py`
  переводит задачу в `solved=false` и возвращает имя изменённого файла.
- AC-4: `python3 -m unittest discover -s evaluation/test -t .` — 76 тестов OK.
- AC-5: `evaluation/README.md`, `evaluation/answer_evaluator/README.md` и
  `specification/behavior/07_evaluation.md` обновлены.
- Дополнительно: 10 задач используют `hidden_unittest`: `coding/solvable/0007`
  (проверка содержимого `readme.txt`) и `coding/solvable/0032`–`0040`
  (программы stdin/stdout). Генератор `data/task_generation/` проверил для
  каждой падение исходного состояния и прохождение эталонной реализации.

## Риски и откат

- Риск: агент прочитает `../tests` и подгонит решение. Митигация: задачи
  сформулированы так, что тесты проверяют поведение на входах, которых нет в
  условии; чтение тестов не отменяет необходимость реализовать алгоритм.
- Риск: `hidden_unittest` случайно запустит видимые тесты. Митигация:
  каталог тестов задан явно, а `iter_test_files` для рабочего каталога не
  меняется.
- Откат: удалить ветку `hidden_unittest` из оценщика и вернуть задачи на
  `exact_int`/`exact_str`.
