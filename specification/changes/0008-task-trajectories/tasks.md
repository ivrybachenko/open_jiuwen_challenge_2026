# Задачи: 0008. Траектории задач для предсказателя сложности

> Архив, не поддерживается. Изменение реализовано; история — в git.

| ID | Задача | Критерий | Статус |
| --- | --- | --- | --- |
| T1 | Добавить `--trajectories-dir` / `TRAJECTORIES_DIR` в конфигурацию и CLI харнесса | AC-1 | done |
| T2 | Включить observability и встроенный `TrajectoryRail` на время прогона; открывать root span задачи | AC-2, AC-3, AC-5 | done |
| T3 | Передавать каталог траекторий из оценщиков в `data/trajectories` | AC-4 | done |
| T4 | Добавить unit-тесты конфигурации и команды оценщика | AC-1, AC-4 | done |
| T5 | Обновить README, `behavior/` и README каталога траекторий | AC-6 | done |
| T6 | Прогнать проверки и записать результат в `spec.md` | AC-1…AC-6 | done |

## Заметки

- Использованы встроенные `acquire_observability`, `TrajectorySpanProcessor`,
  `TrajectoryRail` и `FileTrajectoryStore`.
- Сырые OTLP-файлы observability пишутся во временный каталог, в `data/`
  хранится только канонический JSONL траекторий.
- Понадобилась зависимость `opentelemetry-exporter-otlp-proto-common`:
  без неё модуль observability из openJiuwen не импортируется.
