# Результаты: предсказатели первой волны

Основной набор: 240 строк, 240 задач, 3 прогонов.
Внешний набор: 92 строк, 12 задач.

## Разбиение

Задачи: train=120, val=60, test=60.
Строки: {'train': 120, 'val': 60, 'test': 60}.

## remaining_tokens

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 123.3 | 106.3 | 0.745 |
| turn_overview | random_forest | 123.0 | 93.2 | 0.749 |
| turn_keywords | random_forest | 127.0 | 96.6 | 0.764 |
| full | random_forest_log | 133.2 | 176.0 | 0.333 |

## remaining_turns

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | ridge | 0.0 | 0.0 | 0.956 |
| turn_overview | random_forest | 0.0 | 0.1 | 0.952 |
| turn_keywords | random_forest | 0.0 | 0.1 | 0.926 |
| full | random_forest | 0.0 | 0.1 | 0.920 |

## wave2_cost

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest_log | 319.1 | 227.8 | -2.669 |
| turn_overview | random_forest_log | 309.4 | 231.7 | -2.812 |
| turn_keywords | random_forest_log | 314.8 | 217.4 | -2.203 |
| full | random_forest_log | 306.5 | 301.3 | -5.281 |

## solvable

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 0.757 | 0.837 | 0.923 |
| turn_overview | random_forest | 0.849 | 0.807 | 0.917 |
| turn_keywords | random_forest | 0.699 | 0.756 | 0.878 |
| full | hist_gradient_boosting | 0.910 | 0.797 | 0.912 |

## wave2_any_answer

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | hist_gradient_boosting | 0.710 | 0.778 | 0.977 |
| turn_overview | random_forest | 0.638 | 0.889 | 0.989 |
| turn_keywords | hist_gradient_boosting | 0.710 | 0.778 | 0.977 |
| full | random_forest | 0.509 | 0.556 | 0.947 |

## solved_correctly

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 0.802 | 0.682 | 0.796 |
| turn_overview | hist_gradient_boosting | 0.878 | 0.744 | 0.853 |
| turn_keywords | random_forest | 0.738 | 0.628 | 0.743 |
| full | random_forest | 0.878 | 0.784 | 0.854 |

## wave2_success

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 0.952 | 0.720 | 0.833 |
| turn_overview | random_forest | 0.971 | 0.720 | 0.810 |
| turn_keywords | random_forest | 0.924 | 0.680 | 0.814 |
| full | random_forest | 0.981 | 0.520 | 0.672 |

## Внешняя проверка

### remaining_tokens

- turn/all: n=22, `{"mae": 109.3612121212121, "rmse": 226.015747234523, "medae": 0.0, "bias": 56.92030303030302, "r2": 0.7225597498296036, "spearman": 0.6861237637904527}`
- turn/original_examples: n=20, `{"mae": 70.1745, "rmse": 166.88877468907913, "medae": 0.0, "bias": 12.489500000000007, "r2": 0.8519690729748982, "spearman": 0.6426845869171515}`
- turn_overview/all: n=22, `{"mae": 115.23, "rmse": 228.21970909010403, "medae": 4.1033333333333335, "bias": 57.99757575757574, "r2": 0.7171225264649377, "spearman": 0.6006295513729593}`
- turn_overview/original_examples: n=20, `{"mae": 80.33249999999998, "rmse": 179.3064271095093, "medae": 3.611666666666667, "bias": 17.376833333333337, "r2": 0.8291205173880775, "spearman": 0.5321064319306437}`
- turn_keywords/all: n=22, `{"mae": 112.52378787878791, "rmse": 231.05989820626797, "medae": 1.9633333333333334, "bias": 63.66863636363635, "r2": 0.7100379076037147, "spearman": 0.6107340153974424}`
- turn_keywords/original_examples: n=20, `{"mae": 75.08183333333334, "rmse": 181.50244953504682, "medae": 0.4033333333333333, "bias": 21.34116666666666, "r2": 0.8249092560710592, "spearman": 0.5395637425347116}`
- full/all: n=22, `{"mae": 35.72950334904231, "rmse": 132.6452617901941, "medae": 0.047251395245228256, "bias": -19.46249698970515, "r2": 0.9044401296065274, "spearman": 0.6191555414006602}`
- full/original_examples: n=20, `{"mae": 36.8592402125069, "rmse": 138.7783524969012, "medae": 0.04493137440413796, "bias": -23.851960160115304, "r2": 0.8976373167234744, "spearman": 0.5473436418198936}`

### remaining_turns

- turn/all: n=22, `{"mae": 0.01579592927909945, "rmse": 0.0530805364499801, "medae": 0.0016742033607802798, "bias": 0.015412668474841185, "r2": 0.9760755968190921, "spearman": 0.6046467296186129}`
- turn/original_examples: n=20, `{"mae": 0.003882021479526504, "rmse": 0.0071667356745899816, "medae": 0.0013311335079496667, "bias": 0.0034604345948424154, "r2": 0.9994293099974506, "spearman": 0.5315774339537505}`
- turn_overview/all: n=22, `{"mae": 0.02212121212121212, "rmse": 0.06815016100086958, "medae": 0.0, "bias": 0.02212121212121212, "r2": 0.960562962962963, "spearman": 0.7598342360662242}`
- turn_overview/original_examples: n=20, `{"mae": 0.01, "rmse": 0.0316227766016838, "medae": 0.0, "bias": 0.01, "r2": 0.9888888888888889, "spearman": 0.7453559924999299}`
- turn_keywords/all: n=22, `{"mae": 0.01818181818181818, "rmse": 0.06571287406727709, "medae": 0.0, "bias": 0.01818181818181818, "r2": 0.9633333333333334, "spearman": 0.7598342360662242}`
- turn_keywords/original_examples: n=20, `{"mae": 0.005, "rmse": 0.0158113883008419, "medae": 0.0, "bias": 0.005, "r2": 0.9972222222222222, "spearman": 0.7453559924999299}`
- full/all: n=22, `{"mae": 0.01681818181818182, "rmse": 0.06670832032063166, "medae": 0.0, "bias": 0.01681818181818182, "r2": 0.9622140350877193, "spearman": 0.7598342360662242}`
- full/original_examples: n=20, `{"mae": 0.003, "rmse": 0.009486832980505138, "medae": 0.0, "bias": 0.003, "r2": 0.999, "spearman": 0.7453559924999299}`

### wave2_cost

- turn/all: n=3, `{"mae": 247.79524334070084, "rmse": 400.545309832575, "medae": 25.52933154914706, "bias": -247.79524334070084, "r2": 0.49626298492835996, "spearman": 1.0}`
- turn/original_examples: n=2, `{"mae": 359.1864638163176, "rmse": 490.2468742395233, "medae": 359.1864638163176, "bias": -359.1864638163176, "r2": 0.2843135644690188, "spearman": 0.9999999999999999}`
- turn_overview/all: n=3, `{"mae": 240.56508074579673, "rmse": 396.6122388731654, "medae": 30.680245018937057, "bias": -220.11158406650534, "r2": 0.5061070960587744, "spearman": 1.0}`
- turn_overview/original_examples: n=2, `{"mae": 358.4654009229396, "rmse": 485.73712241278724, "medae": 358.4654009229396, "bias": -327.7851559040025, "r2": 0.2974201165955447, "spearman": 0.9999999999999999}`
- turn_keywords/all: n=3, `{"mae": 245.5587607580343, "rmse": 409.006712807818, "medae": 17.158930730917973, "bias": -245.5587607580343, "r2": 0.47475559524597033, "spearman": 1.0}`
- turn_keywords/original_examples: n=2, `{"mae": 359.7586757715925, "rmse": 500.7819108462996, "medae": 359.7586757715925, "bias": -359.7586757715925, "r2": 0.2532239427763181, "spearman": 0.9999999999999999}`
- full/all: n=3, `{"mae": 298.38100619391133, "rmse": 377.621644053537, "medae": 136.5110184836385, "bias": -118.74397502893312, "r2": 0.5522719328199199, "spearman": 1.0}`
- full/original_examples: n=2, `{"mae": 379.3160000490478, "rmse": 452.30468713337933, "medae": 379.3160000490478, "bias": -246.37147178521894, "r2": 0.3908064507639901, "spearman": 0.9999999999999999}`

### solvable

- turn/all: n=22, `{"accuracy": 0.6363636363636364, "balanced_accuracy": 0.35, "brier": 0.23644343434343432, "log_loss": 0.6641199325407566, "base_rate": 0.9090909090909091, "roc_auc": 0.2, "average_precision": 0.8759186749782725}`
- turn/original_examples: n=20, `{"accuracy": 0.7, "balanced_accuracy": NaN, "brier": 0.19112666666666664, "log_loss": 0.5520905563091763, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn_overview/all: n=22, `{"accuracy": 0.4090909090909091, "balanced_accuracy": 0.225, "brier": 0.3381409090909091, "log_loss": 0.9947977519615321, "base_rate": 0.9090909090909091, "roc_auc": 0.0, "average_precision": 0.7809186749782725}`
- turn_overview/original_examples: n=20, `{"accuracy": 0.45, "balanced_accuracy": NaN, "brier": 0.2791261111111111, "log_loss": 0.7521166892654569, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn_keywords/all: n=22, `{"accuracy": 0.5909090909090909, "balanced_accuracy": 0.325, "brier": 0.2106302576939897, "log_loss": 0.603964275100319, "base_rate": 0.9090909090909091, "roc_auc": 0.325, "average_precision": 0.900624663434261}`
- turn_keywords/original_examples: n=20, `{"accuracy": 0.65, "balanced_accuracy": NaN, "brier": 0.1806373575293765, "log_loss": 0.5384525651347665, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- full/all: n=22, `{"accuracy": 0.045454545454545456, "balanced_accuracy": 0.025, "brier": 0.8171284984832053, "log_loss": 3.4677601082557867, "base_rate": 0.9090909090909091, "roc_auc": 0.0, "average_precision": 0.7825707217618982}`
- full/original_examples: n=20, `{"accuracy": 0.05, "balanced_accuracy": NaN, "brier": 0.8371118018962729, "log_loss": 3.6603533022224175, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`

### wave2_any_answer

- turn/all: n=3, `{"accuracy": 0.6666666666666666, "balanced_accuracy": 0.5, "brier": 0.20182875043118406, "log_loss": 0.5936627095552303, "base_rate": 0.6666666666666666, "roc_auc": 1.0, "average_precision": 1.0}`
- turn/original_examples: n=2, `{"accuracy": 0.5, "balanced_accuracy": 0.5, "brier": 0.23692996623191148, "log_loss": 0.6651555331932748, "base_rate": 0.5, "roc_auc": 1.0, "average_precision": 1.0}`
- turn_overview/all: n=3, `{"accuracy": 0.6666666666666666, "balanced_accuracy": 0.5, "brier": 0.24391481481481478, "log_loss": 0.6809636856941444, "base_rate": 0.6666666666666666, "roc_auc": 0.5, "average_precision": 0.8333333333333333}`
- turn_overview/original_examples: n=2, `{"accuracy": 0.5, "balanced_accuracy": 0.5, "brier": 0.2646222222222222, "log_loss": 0.7225270281634064, "base_rate": 0.5, "roc_auc": 0.0, "average_precision": 0.5}`
- turn_keywords/all: n=3, `{"accuracy": 0.6666666666666666, "balanced_accuracy": 0.5, "brier": 0.20182875043118406, "log_loss": 0.5936627095552303, "base_rate": 0.6666666666666666, "roc_auc": 1.0, "average_precision": 1.0}`
- turn_keywords/original_examples: n=2, `{"accuracy": 0.5, "balanced_accuracy": 0.5, "brier": 0.23692996623191148, "log_loss": 0.6651555331932748, "base_rate": 0.5, "roc_auc": 1.0, "average_precision": 1.0}`
- full/all: n=3, `{"accuracy": 0.3333333333333333, "balanced_accuracy": 0.25, "brier": 0.2714223062244829, "log_loss": 0.7376559098029435, "base_rate": 0.6666666666666666, "roc_auc": 0.0, "average_precision": 0.5833333333333333}`
- full/original_examples: n=2, `{"accuracy": 0.5, "balanced_accuracy": 0.5, "brier": 0.27879057223044984, "log_loss": 0.7532241056451943, "base_rate": 0.5, "roc_auc": 0.0, "average_precision": 0.5}`

