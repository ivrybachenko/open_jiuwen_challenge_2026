# Результаты: предсказатели первой волны

Основной набор: 240 строк, 240 задач, 3 прогонов.
Внешний набор: 92 строк, 12 задач.

## Разбиение

Задачи: train=120, val=60, test=60.
Строки: {'train': 120, 'test': 60, 'val': 60}.

## remaining_tokens

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest_log | 170.9 | 501.5 | 0.092 |
| turn_overview | random_forest_log | 171.0 | 511.3 | 0.031 |
| turn_keywords | random_forest_log | 173.3 | 492.2 | 0.097 |
| full | hist_gradient_boosting_log | 169.1 | 584.3 | -0.003 |

## remaining_turns

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | hist_gradient_boosting | 0.0 | 0.3 | -0.231 |
| turn_overview | hist_gradient_boosting | 0.0 | 0.3 | -0.231 |
| turn_keywords | hist_gradient_boosting | 0.0 | 0.3 | -0.231 |
| full | hist_gradient_boosting | 0.0 | 0.3 | -0.231 |

## wave2_cost

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 388.4 | 529.5 | -0.071 |
| turn_overview | random_forest_log | 385.3 | 589.0 | -0.321 |
| turn_keywords | random_forest | 391.4 | 530.3 | -0.072 |
| full | random_forest_log | 385.4 | 544.4 | -0.165 |

## solvable

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 0.774 | 0.560 | 0.732 |
| turn_overview | random_forest | 0.849 | 0.625 | 0.786 |
| turn_keywords | random_forest | 0.739 | 0.667 | 0.792 |
| full | random_forest | 0.952 | 0.605 | 0.795 |

## wave2_any_answer

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 0.545 | 0.524 | 0.654 |
| turn_overview | random_forest | 0.538 | 0.545 | 0.647 |
| turn_keywords | random_forest | 0.556 | 0.545 | 0.667 |
| full | random_forest | 0.545 | 0.530 | 0.680 |

## solved_correctly

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 0.822 | 0.655 | 0.667 |
| turn_overview | random_forest | 0.835 | 0.588 | 0.663 |
| turn_keywords | random_forest | 0.846 | 0.638 | 0.624 |
| full | random_forest | 0.873 | 0.604 | 0.704 |

## wave2_success

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 0.832 | 0.751 | 0.602 |
| turn_overview | random_forest | 0.853 | 0.792 | 0.714 |
| turn_keywords | random_forest | 0.874 | 0.749 | 0.567 |
| full | random_forest | 0.842 | 0.683 | 0.560 |

## Внешняя проверка

### remaining_tokens

- turn/all: n=22, `{"mae": 395.90706778656914, "rmse": 557.2886649744198, "medae": 311.1735755988001, "bias": -332.2634770859429, "r2": -0.24405011120172548, "spearman": 0.1859808989636916}`
- turn/original_examples: n=21, `{"mae": 414.7597853002153, "rmse": 570.403133732015, "medae": 314.96917024999436, "bias": -348.0855474233687, "r2": -0.4246529832064274, "spearman": 0.06434842187430506}`
- turn_overview/all: n=22, `{"mae": 437.15646615075764, "rmse": 600.1159587298856, "medae": 361.72762689526746, "bias": -389.1341673592296, "r2": -0.44260624148734373, "spearman": 0.10514421643540009}`
- turn_overview/original_examples: n=21, `{"mae": 457.9734407293651, "rmse": 614.2382664069288, "medae": 368.1990804156274, "bias": -407.66436580490716, "r2": -0.6520341640754848, "spearman": -0.02859929861080225}`
- turn_keywords/all: n=22, `{"mae": 388.37771693795656, "rmse": 551.770080514222, "medae": 308.14450174492276, "bias": -327.37454301758413, "r2": -0.21953354180189621, "spearman": 0.14584520344265176}`
- turn_keywords/original_examples: n=21, `{"mae": 406.8718939350022, "rmse": 564.7546824576541, "medae": 311.17904925037976, "bias": -342.96380697080247, "r2": -0.39657726228573664, "spearman": 0.018199553661419614}`
- full/all: n=22, `{"mae": 305.9374796988052, "rmse": 478.56581086595287, "medae": 218.72501211540407, "bias": -146.74985372425124, "r2": 0.08259565456160722, "spearman": 0.08101277646650261}`
- full/original_examples: n=21, `{"mae": 320.5022336116047, "rmse": 489.82772341897703, "medae": 221.22501211540407, "bias": -153.74163949826394, "r2": -0.05058696928927797, "spearman": -0.05004984161021576}`

### remaining_turns

- turn/all: n=22, `{"mae": 0.045454545842574905, "rmse": 0.21320071626285464, "medae": 4.35063318704465e-10, "bias": 0.04545454505155068, "r2": 0.4500000004785696, "spearman": 0.6900655593423541}`
- turn/original_examples: n=21, `{"mae": 0.047619048012676336, "rmse": 0.21821789014105378, "medae": 4.35063318704465e-10, "bias": 0.0476190471839843, "r2": -0.04999999908636665, "spearman": NaN}`
- turn_overview/all: n=22, `{"mae": 0.045454545842574905, "rmse": 0.21320071626285464, "medae": 4.35063318704465e-10, "bias": 0.04545454505155068, "r2": 0.4500000004785696, "spearman": 0.6900655593423541}`
- turn_overview/original_examples: n=21, `{"mae": 0.047619048012676336, "rmse": 0.21821789014105378, "medae": 4.35063318704465e-10, "bias": 0.0476190471839843, "r2": -0.04999999908636665, "spearman": NaN}`
- turn_keywords/all: n=22, `{"mae": 0.045454545842574905, "rmse": 0.21320071626285464, "medae": 4.35063318704465e-10, "bias": 0.04545454505155068, "r2": 0.4500000004785696, "spearman": 0.6900655593423541}`
- turn_keywords/original_examples: n=21, `{"mae": 0.047619048012676336, "rmse": 0.21821789014105378, "medae": 4.35063318704465e-10, "bias": 0.0476190471839843, "r2": -0.04999999908636665, "spearman": NaN}`
- full/all: n=22, `{"mae": 0.045454545842574905, "rmse": 0.21320071626285464, "medae": 4.35063318704465e-10, "bias": 0.04545454505155068, "r2": 0.4500000004785696, "spearman": 0.6900655593423541}`
- full/original_examples: n=21, `{"mae": 0.047619048012676336, "rmse": 0.21821789014105378, "medae": 4.35063318704465e-10, "bias": 0.0476190471839843, "r2": -0.04999999908636665, "spearman": NaN}`

### wave2_cost

- turn/all: n=20, `{"mae": 227.05984548334837, "rmse": 450.7617240421028, "medae": 38.063320310319455, "bias": -95.24395821763149, "r2": -0.008348946599372686, "spearman": -0.1754056196704405}`
- turn/original_examples: n=20, `{"mae": 227.05984548334837, "rmse": 450.7617240421028, "medae": 38.063320310319455, "bias": -95.24395821763149, "r2": -0.008348946599372686, "spearman": -0.1754056196704405}`
- turn_overview/all: n=20, `{"mae": 451.0741550071983, "rmse": 609.2536124038808, "medae": 355.62097140535707, "bias": -416.8045201994557, "r2": -0.8420991924391406, "spearman": -0.21753871600762784}`
- turn_overview/original_examples: n=20, `{"mae": 451.0741550071983, "rmse": 609.2536124038808, "medae": 355.62097140535707, "bias": -416.8045201994557, "r2": -0.8420991924391406, "spearman": -0.21753871600762784}`
- turn_keywords/all: n=20, `{"mae": 224.07061752445497, "rmse": 447.23591372612566, "medae": 33.45820059851462, "bias": -75.57670975381993, "r2": 0.007363757237354607, "spearman": -0.16333469530602307}`
- turn_keywords/original_examples: n=20, `{"mae": 224.07061752445497, "rmse": 447.23591372612566, "medae": 33.45820059851462, "bias": -75.57670975381993, "r2": 0.007363757237354607, "spearman": -0.16333469530602307}`
- full/all: n=20, `{"mae": 362.46159014659617, "rmse": 529.3148658537403, "medae": 250.7831602238304, "bias": -291.5569337255057, "r2": -0.39041667995328955, "spearman": -0.23108784018803372}`
- full/original_examples: n=20, `{"mae": 362.46159014659617, "rmse": 529.3148658537403, "medae": 250.7831602238304, "bias": -291.5569337255057, "r2": -0.39041667995328955, "spearman": -0.23108784018803372}`

### solvable

- turn/all: n=22, `{"accuracy": 0.7272727272727273, "balanced_accuracy": NaN, "brier": 0.15203080808080807, "log_loss": 0.4839630303518721, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn/original_examples: n=21, `{"accuracy": 0.7142857142857143, "balanced_accuracy": NaN, "brier": 0.15730158730158733, "log_loss": 0.496184178334119, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn_overview/all: n=22, `{"accuracy": 0.9545454545454546, "balanced_accuracy": NaN, "brier": 0.1131272727272727, "log_loss": 0.39967433191042867, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn_overview/original_examples: n=21, `{"accuracy": 0.9523809523809523, "balanced_accuracy": NaN, "brier": 0.11641428571428569, "log_loss": 0.4074815699289695, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn_keywords/all: n=22, `{"accuracy": 0.8181818181818182, "balanced_accuracy": NaN, "brier": 0.1412237373737374, "log_loss": 0.4618723275598148, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn_keywords/original_examples: n=21, `{"accuracy": 0.8095238095238095, "balanced_accuracy": NaN, "brier": 0.1443037037037037, "log_loss": 0.4684431469142945, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- full/all: n=22, `{"accuracy": 1.0, "balanced_accuracy": NaN, "brier": 0.04007323232323233, "log_loss": 0.21736460057140866, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- full/original_examples: n=21, `{"accuracy": 1.0, "balanced_accuracy": NaN, "brier": 0.04174814814814815, "log_loss": 0.22425954855886457, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`

### wave2_any_answer

- turn/all: n=20, `{"accuracy": 0.1, "balanced_accuracy": 0.3333333333333333, "brier": 0.4507899999999999, "log_loss": 1.132320735912458, "base_rate": 0.85, "roc_auc": 0.33333333333333337, "average_precision": 0.7673313134385799}`
- turn/original_examples: n=20, `{"accuracy": 0.1, "balanced_accuracy": 0.3333333333333333, "brier": 0.4507899999999999, "log_loss": 1.132320735912458, "base_rate": 0.85, "roc_auc": 0.33333333333333337, "average_precision": 0.7673313134385799}`
- turn_overview/all: n=20, `{"accuracy": 0.1, "balanced_accuracy": 0.3333333333333333, "brier": 0.45806500000000006, "log_loss": 1.1508218372927432, "base_rate": 0.85, "roc_auc": 0.37254901960784315, "average_precision": 0.7824026370238354}`
- turn_overview/original_examples: n=20, `{"accuracy": 0.1, "balanced_accuracy": 0.3333333333333333, "brier": 0.45806500000000006, "log_loss": 1.1508218372927432, "base_rate": 0.85, "roc_auc": 0.37254901960784315, "average_precision": 0.7824026370238354}`
- turn_keywords/all: n=20, `{"accuracy": 0.15, "balanced_accuracy": 0.3627450980392157, "brier": 0.4134455555555555, "log_loss": 1.0472045160655328, "base_rate": 0.85, "roc_auc": 0.3235294117647059, "average_precision": 0.7715410406586878}`
- turn_keywords/original_examples: n=20, `{"accuracy": 0.15, "balanced_accuracy": 0.3627450980392157, "brier": 0.4134455555555555, "log_loss": 1.0472045160655328, "base_rate": 0.85, "roc_auc": 0.3235294117647059, "average_precision": 0.7715410406586878}`
- full/all: n=20, `{"accuracy": 0.1, "balanced_accuracy": 0.3333333333333333, "brier": 0.3870728534453284, "log_loss": 0.9778021175885927, "base_rate": 0.85, "roc_auc": 0.21568627450980393, "average_precision": 0.7606070657928242}`
- full/original_examples: n=20, `{"accuracy": 0.1, "balanced_accuracy": 0.3333333333333333, "brier": 0.3870728534453284, "log_loss": 0.9778021175885927, "base_rate": 0.85, "roc_auc": 0.21568627450980393, "average_precision": 0.7606070657928242}`

