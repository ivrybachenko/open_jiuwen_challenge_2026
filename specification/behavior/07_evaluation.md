# Оценка решения

- Состояние: реализовано
- Проверка: `python -m unittest discover -s evaluation/test -t .`

## Назначение

Пакет `evaluation` измеряет, насколько хорошо харнесс решает задачи. Он
использует только стандартную библиотеку Python и запускает харнесс через
интерпретатор с openJiuwen — по умолчанию `harness/.venv/bin/python`.

## Инструменты

| Команда | Что делает |
| --- | --- |
| `python -m evaluation.answer_evaluator` | Проверяет ответ одной задачи |
| `python -m evaluation.harness_task_checker` | Запускает харнесс на одной задаче |
| `python -m evaluation.harness_task_set_checker` | Запускает харнесс на наборе задач |
| `python -m evaluation.dockerfile_checker` | Собирает образ и прогоняет минимальный набор в контейнере |
| `python -m evaluation.commit_harness_version` | Полный замер версии и запись датасетов |

## Проверка ответа

- Оценщик читает `answer.txt` из копии задачи, а не поле `answer` в
  `solutions.json`: регламент требует файл, а `solved` в JSON означает лишь
  «ответ сдан».
- `unittest`: запускаются все `test*.py`; нужен код возврата 0 и непустой
  `answer.txt`.
- `exact_int`: ответ сравнивается с `expected` как целое. По умолчанию
  допускается один integer внутри текста; `--strict` отключает поблажки.
- `exact_str`: сравнение строк после NFKC, нормализации пробелов, обрезки
  пунктуации и `casefold`; `--strict` отключает поблажки.
- Задачи с `solvable=false` или `impossible=true` баллов не получают.
- Неизвестный `check` даёт 0 баллов.

## Защита от подмены тестов

Перед прогоном оценщик хеширует `test*.py` в рабочем каталоге задачи и после
прогона проверяет, что файлы не изменены и не удалены. При изменении задача
считается нерешённой. Флаг `--allow-test-edits` отключает проверку.

## Стоимость и отчёты

- Стоимость берётся из `solutions.json` (`cost`); если поля нет, применяется
  формула `output + ceil(input / 10)`.
- Отчёты пишутся в `out/reports/*.json`; флаг `--record` обновляет датасеты в
  `data/`.
- `commit_harness_version` делает пять прогонов каждой задачи и набора
  `example`, очищает и заполняет датасеты.
- `dockerfile_checker` проверяет сборку, размеры образа и репозитория, а также
  прогоняет `minimal.yaml` в контейнере.

## Известные ограничения

- Оценщик — локальная модель проверки; скрытые тесты жюри могут отличаться.
- Полные траектории не проверяются, потому что харнесс их не сохраняет.

## Как проверить

```bash
LLM_API_KEY="$NEURAL_DEEP_API_KEY" \
python -m evaluation.harness_task_set_checker \
    --task-set data/task_set/example.yaml --model qwen3.6-35b-a3b
```

Подробности формата отчётов — в [`evaluation/README.md`](../../evaluation/README.md).
