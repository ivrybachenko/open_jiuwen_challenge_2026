# Задачи: 0017. Бюджет из переменной `BUDGET` и лимит по умолчанию

> План выполнения, а не описание текущего поведения. После `implemented`
> файл удаляется или архивируется; история остаётся в git.

| ID | Задача | Критерий | Статус |
| --- | --- | --- | --- |
| T1 | Добавить `DEFAULT_TOKEN_BUDGET = 100000` и чтение только `BUDGET` в `Settings.from_env` | AC-1, AC-2, AC-4 | done |
| T2 | Добавить тесты на приоритет `--budget` и на игнорирование старых псевдонимов | AC-2, AC-3, AC-4 | done |
| T3 | Обновить README, `evaluation/README.md`, `behavior/01_runtime.md`, `behavior/04_budget_and_selection.md` | AC-5 | done |

Статусы: `todo`, `in-progress`, `done`, `cancelled`.

## Заметки

`Settings.budget` остаётся целым числом; `TokenLedger` сохраняет поддержку
`None` для прямого создания в тестах, но `Settings.from_env` больше не
возвращает `None`.
