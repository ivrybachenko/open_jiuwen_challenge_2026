# trajectories

Данные тестовых прогонов харнесса. Начиная с `harness_v0002` здесь лежит
журнал bash-попыток: он нужен для обучения предсказателя сложности и для
разбора решений.

## Как появляется

Оценщики (`harness_task_checker`, `harness_task_set_checker`,
`commit_harness_version`) передают харнессу
`--trajectories-dir <repo>/data/trajectories`. Сам харнесс без этого флага
ничего не пишет, поэтому зачётный запуск по регламенту журнал не создаёт.

Локально можно включить сбор вручную:

```bash
cd harness
uv run python -m harness.run_agent \
  --tasks-dir /tmp/tasks \
  --out /tmp/out/solutions.json \
  --trajectories-dir ../data/trajectories
```

## Файлы v0002

| Файл | Для кого | Что внутри |
| --- | --- | --- |
| `bash_attempts.jsonl` | машины | Одна JSON-строка на ход: задача, волна, обзор, рассуждение, ответ модели, скрипт, вывод, код возврата, расход и признаки. Источник истины. |
| `readable/<task_id>__waveN__<time>.yaml` | человек и машины | Читаемая проекция той же записи: многострочные рассуждения, скрипт и вывод. |

JSONL дописывается и не ротируется. `*.jsonl` и `readable/*.yaml` не хранятся
в git, потому что журнал быстро растёт.

## Поля записи

- `task_id`, `task_type`, `task_path`, `task_root`, `model`;
- `wave`, `turn`, `started_at`, `duration_seconds`;
- `overview` — что агент видел до первого хода;
- `reasoning` — блок рассуждений модели, если провайдер его вернул;
- `content` — сырой ответ модели;
- `script` — скрипт, который реально исполнялся;
- `output`, `exit_code`, `timed_out`, `script_error`;
- `answer`, `answer_kind` (`none`, `value`, `done`, `impossible`);
- `input_tokens`, `output_tokens`, `reasoning_tokens`, `finish_reason`,
  `model_error`;
- `features` — длина рассуждения, ключевые слова, обрыв по лимиту, форма
  скрипта, результат исполнения, вид ответа и категория;
- `run_id`, `logged_at`.

`task_id` — то же значение, под которым задача лежит в `solutions.json`.
Датасетный путь (`coding/solvable/0001`) соединяется с записью через
`task.json` или отчёт оценщика. Если оценщик передал `--run-id`, тот же
идентификатор сохраняется в JSONL и в строке
`data/harness_task_score/` или `data/harness_task_set_score/`.

## Старые данные v0001

`trajectories_default.jsonl` и `readable/*.yaml`, созданные `harness_v0001`,
остаются как история. В них полные канонические траектории openJiuwen с
вызовами инструментов. `harness_v0002` их не пишет: у bash-солвера нет
инструментальных вызовов, а его журнал содержит всё нужное для обучения.

## Как прочитать

JSONL:

```python
import json
from pathlib import Path

for line in Path("data/trajectories/bash_attempts.jsonl").read_text(
    encoding="utf-8"
).splitlines():
    record = json.loads(line)
    if record["task_id"] == "math_0000":
        print(record["wave"], record["answer_kind"], record["features"])
```

YAML:

```python
import yaml
from pathlib import Path

payload = yaml.safe_load(
    Path("data/trajectories/readable/math_0000__wave1__...yaml").read_text(
        encoding="utf-8"
    )
)
print(payload["reasoning"])
print(payload["script"])
```

## Ограничения

- Формат принадлежит харнессу, а не openJiuwen; он меняется вместе с
  `harness/src/harness/application/features.py`.
- Если провайдер не возвращает `reasoning_content`, поле `reasoning` пустое.
- Журнал не ротируется; для длинных серий прогонов его нужно чистить вручную.
