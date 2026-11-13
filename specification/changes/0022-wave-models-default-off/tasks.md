# Задачи: 0022. Выключить модели на волну по умолчанию

| ID | Задача | Критерий | Статус |
| --- | --- | --- | --- |
| T1 | Переключить default `HARNESS_WAVE_MODELS` на 0 | AC-1, AC-3 | done |
| T2 | Обновить тесты default off / явного включения | AC-4 | done |
| T3 | Обновить `01_runtime.md`, `04_budget_and_selection.md`, README | AC-5 | done |
| T4 | Поднять версию до `0007` и записать `harness_info.tsv` | AC-6 | done |

## Заметки

- Артефакты `wave_models.joblib` и `wave_model.json` остаются в образе;
  включаются `HARNESS_WAVE_MODELS=1`.
- Причина default off — кросс-источниковая проверка в `0012` и
  неубедительный живой A/B `0014`.
