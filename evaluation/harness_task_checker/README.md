# harness_task_checker

Запускает харнесс на одной задаче и выдаёт отчёт «решено или нет — сколько
потрачено токенов и времени».

```bash
# значение ключа подставляет bash; Python его не читает и не печатает
export LLM_API_KEY="$NEURAL_DEEP_API_KEY"

# путь относительно data/task или task_id
python -m evaluation.harness_task_checker --task coding/solvable/0001

# явный каталог задачи, ограничения и запись в датасет
python -m evaluation.harness_task_checker \
    --task data/task/math/solvable/0001 \
    --model qwen3.6-35b-a3b \
    --budget 50000 \
    --max-iterations 12 \
    --harness-version 0001 \
    --record
```

`LLM_BASE_URL=https://api.neuraldeep.ru/v1` оценщик подставляет сам; в
харнессе этого URL нет. С `--record` обязателен `--harness-version`, и он
должен совпадать с `harness/pyproject.toml`. Каждая запись получает новый
`run_id` (UUID); задать вручную можно через `--run-id`.

Что происходит:

1. задача копируется во временный каталог (исходный датасет не меняется);
2. для `unittest`-задач запоминаются хеши `test*.py`;
3. запускается `python -m harness.run_agent` на копии;
4. ответ проверяется `answer_evaluator`, тесты перезапускаются, проверяется,
   что агент их не менял;
5. JSON-отчёт пишется в `out/reports/<task_id>.json`.

В отчёте: `solved`, `score`, `verdict`, `tokens` (`input`/`output`/`cost`),
`time_seconds`, команда и хвост логов харнесса. `--keep` оставляет временный
каталог для разбора, `--allow-test-edits` отключает проверку подмены тестов.
`--record` обновляет `data/harness_task_score/harness_v_<version>.tsv` и при
необходимости добавляет версию в `data/harness_info/harness_info.tsv`.

Интерпретатор выбирается так: `--python` → `HARNESS_PYTHON` →
`harness/.venv/bin/python` → текущий Python. Он же используется для повторного
запуска `test*.py`, чтобы тесты видели те же зависимости, что и агент.

Коды возврата: `0` — задача решена, `1` — не решена, `2` — ошибка запуска.
