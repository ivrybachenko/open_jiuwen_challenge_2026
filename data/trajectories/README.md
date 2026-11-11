# trajectories

Полные траектории тестовых прогонов харнесса. Данные нужны для обучения
предсказателя сложности задачи: по ним видно, сколько шагов и инструментов
потребовала задача и как модель рассуждала.

## Как появляется

Оценщики (`harness_task_checker`, `harness_task_set_checker`,
`commit_harness_version`) передают харнессу
`--trajectories-dir <repo>/data/trajectories`. Сам харнесс без этого флага
ничего не пишет, поэтому зачётный запуск по регламенту траектории не создаёт.

Локально можно включить сбор вручную:

```bash
cd harness
uv run python -m harness.run_agent \
  --tasks-dir /tmp/tasks \
  --out /tmp/out/solutions.json \
  --trajectories-dir ../data/trajectories
```

## Файлы

| Файл | Для кого | Что внутри |
| --- | --- | --- |
| `trajectories_default.jsonl` | машины | Одна JSON-строка на задачу: полная каноническая траектория openJiuwen в OTLP-представлении. Источник истины. |
| `readable/<task_id>__<trajectory_id>.yaml` | человек и машины | Читаемая проекция той же траектории: шаги LLM и инструментов, рассуждения, аргументы и результаты. |

JSONL и YAML пишутся вместе. JSONL остаётся главным для обучения: в нём есть
полные prompt-истории, event-span'ы и все атрибуты OTLP. YAML — обзор
решения без повторяющихся prompt-историй и служебных событий.

Файлы дописываются/создаются при каждом прогоне; старые записи не удаляются.
`*.jsonl` и `readable/*.yaml` не хранятся в git, потому что траектории быстро
растут.

## Что сохраняется

Запись создаёт встроенный `TrajectoryRail` из openJiuwen. В ней есть:

- LLM-span'ы: входные сообщения, ответ, `reasoning_content` (часть
  `"type": "reasoning"`), определения инструментов и расход токенов;
- tool-span'ы: имя инструмента, аргументы, результат и ошибка, если вызов
  упал;
- event-span'ы контекста, которые SDK относит к той же траектории.

Ресурсные атрибуты записи содержат `gen_ai.conversation.id` (в API
траектории — `Trajectory.session_id`). Харнесс пишет туда `task_id` из
`task.json`, то есть то же значение, под которым задача лежит в
`solutions.json`. Датасетный путь (`coding/solvable/0001`) соединяется с
траекторией через `task.json` задачи или отчёт оценщика.

Если оценщик передал `--run-id`, тот же идентификатор сохраняется в JSONL как
ресурсный атрибут `harness.run_id`, а в YAML — как поле `run_id`. Это позволяет
однозначно соединить траекторию со строкой
`data/harness_task_score/harness_v_<version>.tsv`: один `run_id` соответствует
одной попытке решения. Для `harness_task_set_score` `run_id` относится ко
всему набору, а задачи внутри набора различаются по `task_id`. Без `--run-id`
поля нет, и связь остаётся только по `task_id`.

## YAML-проекция

Пример структуры:

```yaml
task_id: math_0000
trajectory_id: cf76cba6-67b2-4c11-bb6e-a5233cda78b9
run_id: 3f0c1c5e-...  # только если оценщик передал --run-id
model: qwen3.6-35b-a3b
started_at: '2026-11-10T19:23:33.500Z'
duration_ms: 5840.2
task: |
  A warehouse starts with 1752 boxes...
steps:
  - kind: llm
    started_at: '2026-11-10T19:23:33.500Z'
    duration_ms: 8556.599
    reasoning: |
      Let me trace through this step by step...
    tool_calls:
      - name: bash
        arguments:
          command: |
            python3 -c "..."
    usage:
      prompt_tokens: 3817
      completion_tokens: 380
      total_tokens: 4197
  - kind: tool
    started_at: '2026-11-10T19:23:42.100Z'
    duration_ms: 120.5
    tool: bash
    arguments:
      command: |
        python3 -c "..."
    result: |
      Split into 2: 876
      ...
```

## Как прочитать

YAML:

```python
import yaml
from pathlib import Path

payload = yaml.safe_load(
    Path("data/trajectories/readable/math_0000__<id>.yaml").read_text(
        encoding="utf-8"
    )
)
for step in payload["steps"]:
    if step["kind"] == "llm":
        print(step.get("reasoning"))
```

JSONL (полные данные):

```python
import json
from pathlib import Path

from openjiuwen.agent_evolving.trajectory.model import Trajectory
from openjiuwen.agent_evolving.trajectory.spans import (
    iter_spans,
    read_llm_exchange,
    read_tool_call,
)
from openjiuwen.agent_evolving.trajectory.team import span_category

path = Path("data/trajectories/trajectories_default.jsonl")
for line in path.read_text(encoding="utf-8").splitlines():
    trajectory = Trajectory.from_otlp(json.loads(line))
    for span in iter_spans(trajectory):
        if span_category(span) == "llm":
            prompts, completions = read_llm_exchange(span)
        elif span_category(span) == "tool":
            call = read_tool_call(span)
```

Полный разбор полей — в исходниках установленного openJiuwen
(`openjiuwen/agent_evolving/trajectory/`).
