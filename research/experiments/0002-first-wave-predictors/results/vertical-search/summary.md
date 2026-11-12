# Результаты: предсказатели первой волны

Основной набор: 240 строк, 240 задач, 3 прогонов.
Внешний набор: 92 строк, 12 задач.

## Разбиение

Задачи: train=120, val=60, test=60.
Строки: {'train': 120, 'val': 60, 'test': 60}.

## remaining_tokens

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 116.4 | 267.6 | 0.373 |
| turn_overview | random_forest | 125.9 | 262.3 | 0.364 |
| turn_keywords | random_forest | 135.2 | 257.1 | 0.373 |
| full | random_forest | 142.3 | 272.2 | 0.385 |

## remaining_turns

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | ridge | 0.1 | 0.1 | 0.782 |
| turn_overview | ridge | 0.1 | 0.1 | 0.782 |
| turn_keywords | ridge | 0.1 | 0.1 | 0.784 |
| full | random_forest | 0.1 | 0.0 | 0.957 |

## wave2_cost

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest_log | 208.9 | 395.1 | 0.001 |
| turn_overview | random_forest_log | 213.5 | 395.8 | 0.008 |
| turn_keywords | random_forest_log | 191.9 | 397.1 | -0.013 |
| full | random_forest_log | 199.4 | 391.7 | 0.008 |

## solvable

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | logistic_regression | 0.903 | 0.645 | 0.747 |
| turn_overview | logistic_regression | 0.903 | 0.643 | 0.746 |
| turn_keywords | logistic_regression | 0.950 | 0.640 | 0.761 |
| full | logistic_regression | 1.000 | 0.650 | 0.793 |

## wave2_any_answer

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | logistic_regression | 1.000 | 0.524 | 0.628 |
| turn_overview | logistic_regression | 1.000 | 0.538 | 0.635 |
| turn_keywords | logistic_regression | 1.000 | 0.524 | 0.592 |
| full | logistic_regression | 1.000 | 0.608 | 0.746 |

## solved_correctly

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | logistic_regression | 0.866 | 0.671 | 0.551 |
| turn_overview | logistic_regression | 0.862 | 0.710 | 0.594 |
| turn_keywords | logistic_regression | 0.856 | 0.724 | 0.662 |
| full | logistic_regression | 0.864 | 0.604 | 0.619 |

## wave2_success

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | logistic_regression | 0.760 | 0.600 | 0.329 |
| turn_overview | logistic_regression | 0.720 | 0.589 | 0.325 |
| turn_keywords | logistic_regression | 0.880 | 0.653 | 0.485 |
| full | logistic_regression | 0.880 | 0.379 | 0.385 |

## Внешняя проверка

### remaining_tokens

- turn/all: n=27, `{"mae": 724.6061728395061, "rmse": 1059.7821110564314, "medae": 456.46000000000004, "bias": 13.665185185185145, "r2": -0.06798116475053084, "spearman": 0.2201190683560399}`
- turn/original_examples: n=23, `{"mae": 711.1234782608697, "rmse": 1064.9773382665267, "medae": 456.46000000000004, "bias": 31.722608695652198, "r2": -0.10011095311800289, "spearman": 0.24067211013951872}`
- turn_overview/all: n=27, `{"mae": 729.2665432098767, "rmse": 1064.2735253697147, "medae": 439.11, "bias": -6.992469135802442, "r2": -0.07705267157199636, "spearman": 0.21889788073686633}`
- turn_overview/original_examples: n=23, `{"mae": 717.7884057971014, "rmse": 1070.900434225402, "medae": 439.11, "bias": 21.030144927536252, "r2": -0.1123819803674786, "spearman": 0.21991599386465263}`
- turn_keywords/all: n=27, `{"mae": 728.267037037037, "rmse": 1072.4645334788274, "medae": 536.28, "bias": -2.802839506172825, "r2": -0.09369519074804922, "spearman": 0.171882157398683}`
- turn_keywords/original_examples: n=23, `{"mae": 716.6228985507245, "rmse": 1080.6027237213543, "medae": 536.28, "bias": 25.50666666666665, "r2": -0.1326295067029415, "spearman": 0.18334569376131715}`
- full/all: n=27, `{"mae": 757.4651851851851, "rmse": 1088.0974725847254, "medae": 593.45, "bias": 67.3762962962963, "r2": -0.12581239956850343, "spearman": 0.12120287120297897}`
- full/original_examples: n=23, `{"mae": 752.6363768115941, "rmse": 1090.3789890177197, "medae": 593.45, "bias": 96.73985507246378, "r2": -0.1532161196493338, "spearman": 0.12799605036167425}`

### remaining_turns

- turn/all: n=27, `{"mae": 0.0017597154490087922, "rmse": 0.0021005791604225086, "medae": 0.0014712246704955412, "bias": -0.0007080018093144501, "r2": 0.9999356667296418, "spearman": 0.4539206495016018}`
- turn/original_examples: n=23, `{"mae": 0.001787934810117855, "rmse": 0.0021535940172759524, "medae": 0.0014854093364642385, "bias": -0.0008724243620734096, "r2": 0.9999415836989484, "spearman": 0.48850421045919723}`
- turn_overview/all: n=27, `{"mae": 0.0018380432714138533, "rmse": 0.002111081641400995, "medae": 0.0015451336828085083, "bias": -0.0008135666661934647, "r2": 0.9999350218141427, "spearman": 0.4539206495016018}`
- turn_overview/original_examples: n=23, `{"mae": 0.0018574370825872031, "rmse": 0.002155058567810834, "medae": 0.0015229997311952959, "bias": -0.0009640771451233075, "r2": 0.9999415042199801, "spearman": 0.48850421045919723}`
- turn_keywords/all: n=27, `{"mae": 0.0036287341767040214, "rmse": 0.008483211342253532, "medae": 0.0018329851351073234, "bias": 0.0005593771681100945, "r2": 0.9989507521272044, "spearman": 0.4539206495016018}`
- turn_keywords/original_examples: n=23, `{"mae": 0.003875100276545797, "rmse": 0.009124357413536035, "medae": 0.0018438398073097328, "bias": 0.0005778663932522634, "r2": 0.998951397329689, "spearman": 0.48850421045919723}`
- full/all: n=27, `{"mae": 0.022592592592592588, "rmse": 0.1078312200453139, "medae": 0.0, "bias": -0.021111111111111105, "r2": 0.83047, "spearman": 0.5155075474676031}`
- full/original_examples: n=23, `{"mae": 0.026376811594202895, "rmse": 0.11683011325133107, "medae": 0.0, "bias": -0.024637681159420284, "r2": 0.828084126984127, "spearman": 0.5451887464271151}`

### wave2_cost

- turn/all: n=24, `{"mae": 672.8147814294159, "rmse": 1114.3243781493886, "medae": 339.3224081826082, "bias": -409.6529049266507, "r2": -0.1470104607147691, "spearman": -0.013913043478260868}`
- turn/original_examples: n=20, `{"mae": 647.001348335476, "rmse": 1127.1438687563627, "medae": 317.815509680636, "bias": -369.8848956057897, "r2": -0.17982599636264562, "spearman": -0.045112781954887216}`
- turn_overview/all: n=24, `{"mae": 669.6586493055817, "rmse": 1111.6237981820698, "medae": 356.539793439781, "bias": -395.16416625465314, "r2": -0.14145760733802137, "spearman": -0.07652173913043478}`
- turn_overview/original_examples: n=20, `{"mae": 642.7140334096001, "rmse": 1124.3690075656027, "medae": 294.99537232189937, "bias": -353.1186425373477, "r2": -0.17402403338551875, "spearman": -0.08872180451127819}`
- turn_keywords/all: n=24, `{"mae": 674.5998613618632, "rmse": 1116.0240766198385, "medae": 344.9878638609128, "bias": -414.238858777403, "r2": -0.15051223958994941, "spearman": 0.042608695652173914}`
- turn_keywords/original_examples: n=20, `{"mae": 649.4616805421427, "rmse": 1128.481667052747, "medae": 316.9045237954506, "bias": -373.27461185069905, "r2": -0.18262831100732124, "spearman": -0.006015037593984962}`
- full/all: n=24, `{"mae": 674.9360216080056, "rmse": 1113.4994192220074, "medae": 347.80829301659446, "bias": -411.84979385473616, "r2": -0.14531277505334805, "spearman": -0.06695652173913043}`
- full/original_examples: n=20, `{"mae": 646.1391038391743, "rmse": 1123.1196292603738, "medae": 318.42390303831763, "bias": -370.4934539582765, "r2": -0.17141637485617012, "spearman": -0.11729323308270674}`

### solvable

- turn/all: n=27, `{"accuracy": 0.1111111111111111, "balanced_accuracy": NaN, "brier": 0.5036033594438432, "log_loss": 1.2881427659319664, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn/original_examples: n=23, `{"accuracy": 0.13043478260869565, "balanced_accuracy": NaN, "brier": 0.49110763320550416, "log_loss": 1.2548045097723344, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn_overview/all: n=27, `{"accuracy": 0.1111111111111111, "balanced_accuracy": NaN, "brier": 0.5124655813549636, "log_loss": 1.3127583212896883, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn_overview/original_examples: n=23, `{"accuracy": 0.13043478260869565, "balanced_accuracy": NaN, "brier": 0.49930047644713266, "log_loss": 1.2775269309733353, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn_keywords/all: n=27, `{"accuracy": 0.14814814814814814, "balanced_accuracy": NaN, "brier": 0.48349041233999235, "log_loss": 1.2296353031378955, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn_keywords/original_examples: n=23, `{"accuracy": 0.17391304347826086, "balanced_accuracy": NaN, "brier": 0.48569249345610704, "log_loss": 1.2332002435719147, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- full/all: n=27, `{"accuracy": 0.5185185185185185, "balanced_accuracy": NaN, "brier": 0.2889017292568174, "log_loss": 0.7951696217745275, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- full/original_examples: n=23, `{"accuracy": 0.6086956521739131, "balanced_accuracy": NaN, "brier": 0.22418609650763582, "log_loss": 0.6352220373520907, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`

### wave2_any_answer

- turn/all: n=24, `{"accuracy": 0.4583333333333333, "balanced_accuracy": 0.5214285714285715, "brier": 0.29124572499182444, "log_loss": 0.8001545846807953, "base_rate": 0.5833333333333334, "roc_auc": 0.40714285714285714, "average_precision": 0.5752533655095766}`
- turn/original_examples: n=20, `{"accuracy": 0.45, "balanced_accuracy": 0.5208333333333334, "brier": 0.30065732278659224, "log_loss": 0.823890544306634, "base_rate": 0.6, "roc_auc": 0.34375, "average_precision": 0.5626980189286691}`
- turn_overview/all: n=24, `{"accuracy": 0.4583333333333333, "balanced_accuracy": 0.4642857142857143, "brier": 0.289222642463002, "log_loss": 0.7970746771410689, "base_rate": 0.5833333333333334, "roc_auc": 0.36428571428571427, "average_precision": 0.5368049733321929}`
- turn_overview/original_examples: n=20, `{"accuracy": 0.4, "balanced_accuracy": 0.39583333333333337, "brier": 0.29879302035477173, "log_loss": 0.8213138199388824, "base_rate": 0.6, "roc_auc": 0.2916666666666667, "average_precision": 0.528077546808197}`
- turn_keywords/all: n=24, `{"accuracy": 0.4166666666666667, "balanced_accuracy": 0.4714285714285714, "brier": 0.2942398811417039, "log_loss": 0.8040739942584701, "base_rate": 0.5833333333333334, "roc_auc": 0.37857142857142856, "average_precision": 0.5374828027390139}`
- turn_keywords/original_examples: n=20, `{"accuracy": 0.45, "balanced_accuracy": 0.5208333333333334, "brier": 0.2996883696563219, "log_loss": 0.8194223574963988, "base_rate": 0.6, "roc_auc": 0.35416666666666663, "average_precision": 0.56865039988105}`
- full/all: n=24, `{"accuracy": 0.4166666666666667, "balanced_accuracy": 0.5, "brier": 0.4129908290795204, "log_loss": 1.1679812042657194, "base_rate": 0.5833333333333334, "roc_auc": 0.4, "average_precision": 0.5598603223273915}`
- full/original_examples: n=20, `{"accuracy": 0.4, "balanced_accuracy": 0.5, "brier": 0.43465922538244256, "log_loss": 1.2384281192069904, "base_rate": 0.6, "roc_auc": 0.39583333333333337, "average_precision": 0.6109910861555599}`

