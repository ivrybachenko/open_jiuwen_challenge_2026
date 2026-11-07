# answer_evaluator

Библиотека, которая понимает проверки `unittest`, `exact_int` и `exact_str` и
выдаёт вердикт: правильно ли харнесс решил задачу. Не доверяет полю `solved`
из `solutions.json` — там оно означает только «ответ сдан».

```bash
# задача в формате data/task/...
python -m evaluation.answer_evaluator --task data/task/coding/easy/0001

# краткий путь относительно data/task или task_id
python -m evaluation.answer_evaluator --task coding/easy/0001
python -m evaluation.answer_evaluator --task data_analysis_0002

# можно подставить готовый ответ вместо answer.txt
python -m evaluation.answer_evaluator \
    --task data_analysis/easy/0001 --answer /tmp/answer.txt
```

Правила проверок:

- `exact_int` — ответ сравнивается как целое число. По умолчанию разрешены
  пробелы, запятые и подчёркивания как разделители тысяч, а также ответ вида
  «The answer is 42» при наличии ровно одного числа. Флаг `--strict`
  отключает эти послабления.
- `exact_str` — сравнение после нормализации Unicode, схлопывания пробелов,
  удаления кавычек/обратных кавычек и завершающей пунктуации. По умолчанию
  регистр не важен; `--strict` делает сравнение регистрозависимым.
- `unittest` — в `workspace/` ищутся файлы `test*.py`, каждый запускается
  интерпретатором из `--python` (по умолчанию текущим). Задача решена, если
  все тесты завершились с кодом `0` **и** был сдан `answer.txt`.
- Невыполнимые задачи (`check` = `none`/`unsolvable`/`impossible`, либо
  `"solvable": false` / `"impossible": true` в `task.json`) баллов не
  приносят: оценщик возвращает `solved=false`.

`--out` сохраняет вердикт в JSON.
