# harness_task_set_score

Баллы и стоимость решения набора задач для конкретной версии харнесса. Один
файл на версию: `harness_v_<version>.tsv`.

| Поле | Описание |
| --- | --- |
| `harness_version` | Версия харнесса из `harness/pyproject.toml`. |
| `run_id` | Уникальный идентификатор строки — UUID. Генерируется заново для каждого записанного результата, поэтому двух строк с одним `run_id` в файле нет. |
| `task_set_id` | Имя набора — имя YAML-файла без расширения (`minimal`, `example`). |
| `score` | Сумма `reward` задач, которые прошли проверку оценщика. Поле `solved` из `solutions.json` не используется. |
| `cost_tokens` | Суммарная стоимость в выходных токенах по всем задачам набора: `output + ceil(input / 10)`. |
| `cost_seconds` | Время работы харнесса на всём наборе, секунды. |

Формат — TSV, одна строка на один результат. `run_id` уникален в пределах
файла. Повторная запись той же пары (`run_id`, `task_set_id`) обновляет
строку; тот же `run_id` для другого набора отклоняется с ошибкой.

Заполнение:

```bash
LLM_API_KEY="$NEURAL_DEEP_API_KEY" \
python -m evaluation.harness_task_set_checker \
    --task-set data/task_set/example.yaml \
    --model qwen3.6-35b-a3b \
    --harness-version 0001 \
    --record
```

`--harness-version` обязателен вместе с `--record` и должен совпадать с
`harness/pyproject.toml`. `run_id` можно задать через `--run-id`, иначе
генерируется случайный UUID.

Полный замер версии — 5 прогонов каждой задачи и 5 прогонов набора `example`:

```bash
LLM_API_KEY="$NEURAL_DEEP_API_KEY" \
python -m evaluation.commit_harness_version --harness-version 0001
```

Для `dockerfile_checker` можно записать результат контейнерного прогона:

```bash
LLM_API_KEY="$NEURAL_DEEP_API_KEY" \
python -m evaluation.dockerfile_checker --harness-version 0001 --record
```

`cost_seconds` в этом случае — время `docker run`, без сборки образа.

Текущие значения в `harness_v_0001.tsv` получены скриптом
`commit_harness_version` локальным прогоном харнесса (модель
`qwen3.6-35b-a3b`, `https://api.neuraldeep.ru/v1`), а не в Docker. При
переходе на уникальные `run_id` исторические значения заменены на UUID; баллы,
стоимость и время не менялись.
