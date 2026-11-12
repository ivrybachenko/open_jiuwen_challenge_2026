# Результаты: предсказатели первой волны

Основной набор: 240 строк, 240 задач, 3 прогонов.
Внешний набор: 92 строк, 12 задач.

## Разбиение

Задачи: train=120, val=60, test=60.
Строки: {'train': 120, 'val': 60, 'test': 60}.

## remaining_tokens

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest_log | 413.4 | 113.9 | 0.607 |
| turn_overview | random_forest_log | 420.7 | 112.4 | 0.620 |
| turn_keywords | random_forest_log | 410.2 | 126.7 | 0.562 |
| full | random_forest_log | 402.4 | 102.2 | 0.673 |

## remaining_turns

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | ridge | 0.1 | 0.1 | 0.978 |
| turn_overview | ridge | 0.1 | 0.1 | 0.979 |
| turn_keywords | ridge | 0.1 | 0.1 | 0.971 |
| full | random_forest_log | 0.1 | 0.0 | 0.999 |

## wave2_cost

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 522.4 | 270.2 | -0.072 |
| turn_overview | random_forest | 523.2 | 268.6 | -0.059 |
| turn_keywords | random_forest | 521.8 | 272.9 | -0.079 |
| full | random_forest | 523.7 | 287.8 | -0.065 |

## solvable

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 0.572 | 0.677 | 0.809 |
| turn_overview | random_forest | 0.579 | 0.744 | 0.872 |
| turn_keywords | random_forest | 0.703 | 0.695 | 0.824 |
| full | logistic_regression | 0.666 | 0.789 | 0.863 |

## wave2_any_answer

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | logistic_regression | 0.581 | 0.384 | 0.632 |
| turn_overview | logistic_regression | 0.638 | 0.375 | 0.642 |
| turn_keywords | logistic_regression | 0.583 | 0.464 | 0.676 |
| full | logistic_regression | 0.623 | 0.446 | 0.679 |

## solved_correctly

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 0.556 | 0.823 | 0.824 |
| turn_overview | logistic_regression | 0.583 | 0.611 | 0.683 |
| turn_keywords | random_forest | 0.637 | 0.796 | 0.811 |
| full | hist_gradient_boosting | 0.661 | 0.826 | 0.901 |

## wave2_success

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 0.669 | 0.733 | 0.677 |
| turn_overview | random_forest | 0.718 | 0.724 | 0.621 |
| turn_keywords | random_forest | 0.667 | 0.724 | 0.584 |
| full | random_forest | 0.708 | 0.667 | 0.648 |

## Внешняя проверка

### remaining_tokens

- turn/all: n=21, `{"mae": 36.5990424571061, "rmse": 92.79405234468463, "medae": 0.004289168885381202, "bias": 31.36095237471134, "r2": 0.8889810869798863, "spearman": 0.7265420070594026}`
- turn/original_examples: n=19, `{"mae": 27.805657711230406, "rmse": 86.89818139823839, "medae": 0.004289168885381202, "bias": 27.805657711230406, "r2": 0.759517217625854, "spearman": 0.5797409637607477}`
- turn_overview/all: n=21, `{"mae": 35.72634764770174, "rmse": 106.12390711421926, "medae": 0.013507589444078663, "bias": 35.72634764770174, "r2": 0.8547944718861659, "spearman": 0.6819736044954727}`
- turn_overview/original_examples: n=19, `{"mae": 32.68020286154283, "rmse": 108.64385565781987, "medae": 0.013507589444078663, "bias": 32.68020286154283, "r2": 0.6240994575000789, "spearman": 0.5352309301050473}`
- turn_keywords/all: n=21, `{"mae": 28.32962592939645, "rmse": 78.31905726799025, "medae": 0.01580735476146179, "bias": 16.412284197871553, "r2": 0.9209154602615117, "spearman": 0.6853254138995912}`
- turn_keywords/original_examples: n=19, `{"mae": 21.936896546740826, "rmse": 76.20798874365578, "medae": 0.01321860194141142, "bias": 21.936896546740826, "r2": 0.81504604916832, "spearman": 0.5347583199200759}`
- full/all: n=21, `{"mae": 69.99863004880133, "rmse": 186.93152063612197, "medae": 0.0, "bias": 69.99863004880133, "r2": 0.5494720212662207, "spearman": 0.9917127071823205}`
- full/original_examples: n=19, `{"mae": 55.44634995883297, "rmse": 183.11831137568402, "medae": 0.0, "bias": 55.44634995883297, "r2": -0.06788912154383975, "spearman": 1.0}`

### remaining_turns

- turn/all: n=21, `{"mae": 0.058130504935839857, "rmse": 0.061276516014269984, "medae": 0.0563583479990889, "bias": 0.03714710772190364, "r2": 0.9756489436184181, "spearman": 0.6809084840390547}`
- turn/original_examples: n=19, `{"mae": 0.05989769420534905, "rmse": 0.06292728475394263, "medae": 0.058214675863770826, "bias": 0.04540914083742007, "r2": 0.9579557828497687, "spearman": 0.532290647422377}`
- turn_overview/all: n=21, `{"mae": 0.07019538012050426, "rmse": 0.07410692072582951, "medae": 0.07340396681618139, "bias": 0.05570787881080111, "r2": 0.9643838302431795, "spearman": 0.6809084840390547}`
- turn_overview/original_examples: n=19, `{"mae": 0.07513340275919214, "rmse": 0.07753736633886218, "medae": 0.07572311339214172, "bias": 0.061864192738758615, "r2": 0.9361662474254453, "spearman": 0.532290647422377}`
- turn_keywords/all: n=21, `{"mae": 0.06386886700718969, "rmse": 0.07506183940784025, "medae": 0.06696564713336528, "bias": 0.033385879213192166, "r2": 0.9634600387755561, "spearman": 0.6809084840390547}`
- turn_keywords/original_examples: n=19, `{"mae": 0.062056914589014155, "rmse": 0.07352528566166443, "medae": 0.06696564713336528, "bias": 0.040590232849192345, "r2": 0.9426013436759354, "spearman": 0.532290647422377}`
- full/all: n=21, `{"mae": 0.00011015056391354228, "rmse": 0.0005047732969733591, "medae": 0.0, "bias": 0.00011015056391354228, "r2": 0.9999983475724725, "spearman": 0.916515138991168}`
- full/original_examples: n=19, `{"mae": 0.00012174536011466394, "rmse": 0.000530675721583463, "medae": 0.0, "bias": 0.00012174536011466394, "r2": 0.9999970098930455, "spearman": 0.838870492807861}`

### wave2_cost

- turn/all: n=4, `{"mae": 400.7674585671473, "rmse": 455.88883204557334, "medae": 303.87054677173285, "bias": 400.7674585671473, "r2": -2.665481383477694, "spearman": 0.19999999999999998}`
- turn/original_examples: n=2, `{"mae": 545.373984160818, "rmse": 590.7198286313816, "medae": 545.373984160818, "bias": 545.373984160818, "r2": -4.142184355912169, "spearman": 0.9999999999999999}`
- turn_overview/all: n=4, `{"mae": 425.4785233273134, "rmse": 479.1579938820447, "medae": 327.0899586880265, "bias": 425.4785233273134, "r2": -3.04921267186472, "spearman": 0.19999999999999998}`
- turn_overview/original_examples: n=2, `{"mae": 576.4948004554276, "rmse": 618.9094769310049, "medae": 576.4948004554276, "bias": 576.4948004554276, "r2": -4.64467329010739, "spearman": 0.9999999999999999}`
- turn_keywords/all: n=4, `{"mae": 396.1590179068828, "rmse": 451.41124618853087, "medae": 297.75712207397976, "bias": 396.1590179068828, "r2": -2.593832738432332, "spearman": 0.39999999999999997}`
- turn_keywords/original_examples: n=2, `{"mae": 537.8889788801414, "rmse": 584.6131264600365, "medae": 537.8889788801414, "bias": 537.8889788801414, "r2": -4.036416865976453, "spearman": 0.9999999999999999}`
- full/all: n=4, `{"mae": 440.34514028799697, "rmse": 491.4414071889451, "medae": 341.6244034907993, "bias": 440.34514028799697, "r2": -3.2594801932937196, "spearman": 0.19999999999999998}`
- full/original_examples: n=2, `{"mae": 589.1742840345642, "rmse": 630.3476280266083, "medae": 589.1742840345642, "bias": 589.1742840345642, "r2": -4.855241207610807, "spearman": 0.9999999999999999}`

### solvable

- turn/all: n=21, `{"accuracy": 0.9047619047619048, "balanced_accuracy": NaN, "brier": 0.11034973544973543, "log_loss": 0.3816243700387782, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn/original_examples: n=19, `{"accuracy": 0.9473684210526315, "balanced_accuracy": NaN, "brier": 0.10120760233918129, "log_loss": 0.3653245909944637, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn_overview/all: n=21, `{"accuracy": 0.8095238095238095, "balanced_accuracy": NaN, "brier": 0.1887835978835979, "log_loss": 0.56089877554535, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn_overview/original_examples: n=19, `{"accuracy": 0.8421052631578947, "balanced_accuracy": NaN, "brier": 0.1788578947368421, "log_loss": 0.5399432389746203, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn_keywords/all: n=21, `{"accuracy": 1.0, "balanced_accuracy": NaN, "brier": 0.06457354497354498, "log_loss": 0.27673407575003434, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn_keywords/original_examples: n=19, `{"accuracy": 1.0, "balanced_accuracy": NaN, "brier": 0.05970643274853801, "log_loss": 0.26852768968891333, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- full/all: n=21, `{"accuracy": 0.9523809523809523, "balanced_accuracy": NaN, "brier": 0.04539020355209266, "log_loss": 0.14886885928982987, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- full/original_examples: n=19, `{"accuracy": 0.9473684210526315, "balanced_accuracy": NaN, "brier": 0.04508202509840895, "log_loss": 0.14286792641827617, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`

### wave2_any_answer

- turn/all: n=4, `{"accuracy": 0.5, "balanced_accuracy": 0.3333333333333333, "brier": 0.34921628195474624, "log_loss": 0.9445466419875163, "base_rate": 0.75, "roc_auc": 0.6666666666666666, "average_precision": 0.9166666666666665}`
- turn/original_examples: n=2, `{"accuracy": 0.5, "balanced_accuracy": 0.5, "brier": 0.3073173283434182, "log_loss": 0.8024497943964644, "base_rate": 0.5, "roc_auc": 1.0, "average_precision": 1.0}`
- turn_overview/all: n=4, `{"accuracy": 0.5, "balanced_accuracy": 0.3333333333333333, "brier": 0.4039202807205252, "log_loss": 1.411879274072227, "base_rate": 0.75, "roc_auc": 0.6666666666666666, "average_precision": 0.9166666666666665}`
- turn_overview/original_examples: n=2, `{"accuracy": 0.5, "balanced_accuracy": 0.5, "brier": 0.32268805681692597, "log_loss": 0.8504678600893021, "base_rate": 0.5, "roc_auc": 1.0, "average_precision": 1.0}`
- turn_keywords/all: n=4, `{"accuracy": 0.5, "balanced_accuracy": 0.3333333333333333, "brier": 0.34169967591247713, "log_loss": 1.588827845594779, "base_rate": 0.75, "roc_auc": 0.3333333333333333, "average_precision": 0.8055555555555556}`
- turn_keywords/original_examples: n=2, `{"accuracy": 0.5, "balanced_accuracy": 0.5, "brier": 0.5177075986165738, "log_loss": 2.748940458877343, "base_rate": 0.5, "roc_auc": 0.0, "average_precision": 0.5}`
- full/all: n=4, `{"accuracy": 0.75, "balanced_accuracy": 0.5, "brier": 0.24980325755460742, "log_loss": 1.862105308838139, "base_rate": 0.75, "roc_auc": 0.0, "average_precision": 0.6388888888888888}`
- full/original_examples: n=2, `{"accuracy": 0.5, "balanced_accuracy": 0.5, "brier": 0.49940522119000447, "log_loss": 3.7135090767521532, "base_rate": 0.5, "roc_auc": 0.0, "average_precision": 0.5}`

