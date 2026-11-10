# harness_task_score

Стоимость решения отдельных задач для конкретной версии харнесса. Один файл
на версию: `harness_v_<version>.tsv` (например, `harness_v_0001.tsv`).

| Поле | Описание |
| --- | --- |
| `harness_version` | Версия харнесса из `harness/pyproject.toml`. |
| `run_id` | Идентификатор запуска. Каждый запуск чекера получает новый `run_id` (UTC-время с микросекундами), поэтому повторные прогоны не перезаписывают друг друга. |
| `task_id` | Путь задачи в датасете относительно `data/task`, например `coding/solvable/0001`. Это не поле `task_id` из `task.json` (там `coding_0003`), а имя каталога задачи. |
| `is_solved_correctly` | `true`/`false` — вердикт `answer_evaluator`: ответ сдан и проверка `unittest`/`exact_int`/`exact_str` пройдена, тесты не подменены. Поле `solved` из `solutions.json` не используется. |
| `cost_tokens` | Стоимость в выходных токенах: `output_tokens + ceil(input_tokens / 10)`. Берётся из поля `cost` в `solutions.json`. |
| `cost_seconds` | Время работы харнесса на этой задаче, секунды (замер чекера, не время отдельного LLM-вызова). |

Формат — TSV, одна строка на (`harness_version`, `run_id`, `task_id`).
Повторный запуск с новым `run_id` добавляет ещё одну строку для той же задачи;
повторная запись того же `run_id` обновляет строку.

Заполнение:

```bash
# значение ключа подставляет bash, Python его не читает и не печатает
LLM_API_KEY="$NEURAL_DEEP_API_KEY" \
python -m evaluation.harness_task_checker \
    --task coding/solvable/0001 \
    --model qwen3.6-35b-a3b \
    --harness-version 0001 \
    --record
```

`--harness-version` обязателен вместе с `--record` и должен совпадать с
`harness/pyproject.toml`, иначе команда завершится ошибкой. `run_id` можно
задать явно через `--run-id`, иначе он генерируется автоматически.

Для полного замера версии (5 прогонов каждой задачи и 5 прогонов набора
`example`) используйте:

```bash
LLM_API_KEY="$NEURAL_DEEP_API_KEY" \
python -m evaluation.commit_harness_version --harness-version 0001
```

Текущие значения в `harness_v_0001.tsv` получены именно этим скриптом:
`qwen3.6-35b-a3b`, `https://api.neuraldeep.ru/v1`, 5 повторов.
