# harness_task_set_checker

Запускает харнесс на наборе задач из `data/task_set/*.yaml` и выдаёт отчёт
«сколько баллов набрано — сколько потрачено токенов и времени».

```bash
# значение ключа подставляет bash; Python его не читает и не печатает
export LLM_API_KEY="$NEURAL_DEEP_API_KEY"

python -m evaluation.harness_task_set_checker \
    --task-set data/task_set/example.yaml \
    --model qwen3.6-35b-a3b --harness-version 0001 --record

# быстрый прогон только первых двух задач
python -m evaluation.harness_task_set_checker \
    --task-set minimal.yaml --max-tasks 2 --budget 50000
```

`LLM_BASE_URL=https://api.neuraldeep.ru/v1` оценщик подставляет сам; в
харнессе этого URL нет. С `--record` обязателен `--harness-version`, и он
должен совпадать с `harness/pyproject.toml`. Каждая запись получает новый
`run_id` (UUID); задать вручную можно через `--run-id`. `--record` обновляет
`data/harness_task_set_score/harness_v_<version>.tsv`.

Набор читается из YAML вида:

```yaml
dataset:
  random_seed: 42
  tasks:
    - coding/solvable/0001
    - data_analysis/solvable/0001
```

Пути задач разрешаются относительно `data/task` (переопределяется
`--tasks-root`). Задачи копируются в плоский временный каталог, чтобы
`harness.run_agent` видел их как `<tasks-dir>/<task>/task.json`; исходный
датасет не меняется.

Отчёт (`out/reports/<имя_набора>.json`) содержит:

- `summary.score` / `summary.max_score` — баллы только за реально решённые
  задачи (проверенные оценщиком, а не полем `solved` харнесса);
- `summary.solved_tasks` / `summary.total_tasks`;
- `summary.input_tokens`, `summary.output_tokens`, `summary.cost`;
- `time_seconds` — время прогона харнесса;
- `tasks[]` — вердикт и стоимость по каждой задаче.

Флаги `--fail-on-unsolved` и `--min-score` превращают отчёт в проверку для CI.
Коды возврата: `0` — успех, `1` — не выполнено условие, `2` — ошибка запуска.
