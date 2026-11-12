# Результаты: предсказатели первой волны

Основной набор: 240 строк, 240 задач, 3 прогонов.
Внешний набор: 92 строк, 12 задач.

## Разбиение

Задачи: train=136, val=45, test=59.
Строки: {'train': 136, 'test': 59, 'val': 45}.

## remaining_tokens

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 277.6 | 194.9 | 0.415 |
| turn_overview | random_forest | 279.3 | 195.1 | 0.414 |
| turn_keywords | random_forest | 273.3 | 191.0 | 0.427 |
| full | random_forest_log | 283.6 | 158.9 | 0.427 |

## remaining_turns

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | ridge | 0.0 | 0.0 | 0.999 |
| turn_overview | ridge | 0.0 | 0.0 | 0.999 |
| turn_keywords | ridge | 0.0 | 0.0 | 0.999 |
| full | random_forest_log | 0.0 | 0.0 | 0.996 |

## wave2_cost

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 547.5 | 440.2 | -0.277 |
| turn_overview | ridge | 549.2 | 303.3 | -0.004 |
| turn_keywords | ridge | 551.7 | 295.6 | -0.007 |
| full | ridge | 579.3 | 324.2 | -0.064 |

## solvable

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 0.855 | 0.804 | 0.909 |
| turn_overview | hist_gradient_boosting | 0.869 | 0.738 | 0.887 |
| turn_keywords | logistic_regression | 0.875 | 0.817 | 0.869 |
| full | random_forest | 0.925 | 0.973 | 0.991 |

## wave2_any_answer

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | logistic_regression | 0.857 | 0.229 | 0.549 |
| turn_overview | logistic_regression | 0.940 | 0.167 | 0.492 |
| turn_keywords | logistic_regression | 0.726 | 0.236 | 0.535 |
| full | logistic_regression | 0.667 | 0.417 | 0.642 |

## solved_correctly

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 0.935 | 0.798 | 0.831 |
| turn_overview | logistic_regression | 0.929 | 0.761 | 0.778 |
| turn_keywords | random_forest | 0.932 | 0.838 | 0.886 |
| full | random_forest | 0.978 | 0.861 | 0.867 |

## wave2_success

| Набор признаков | Модель | Val MAE/AUC | Test MAE/AUC | Test R²/AP |
| --- | --- | ---: | ---: | ---: |
| turn | random_forest | 1.000 | 0.682 | 0.725 |
| turn_overview | logistic_regression | 0.960 | 0.494 | 0.574 |
| turn_keywords | random_forest | 1.000 | 0.688 | 0.721 |
| full | random_forest | 0.980 | 0.773 | 0.799 |

## Внешняя проверка

### remaining_tokens

- turn/all: n=92, `{"mae": 257.51373188405796, "rmse": 573.0524567631611, "medae": 36.08499999999998, "bias": -79.40865942028987, "r2": 0.4537952484202936, "spearman": 0.8381209678337748}`
- turn/original_examples: n=83, `{"mae": 237.29919678714862, "rmse": 562.7567352493801, "medae": 14.690000000000055, "bias": -85.6269076305221, "r2": 0.4466477002549546, "spearman": 0.8426970296869398}`
- turn_overview/all: n=92, `{"mae": 255.23184782608695, "rmse": 570.6683493967937, "medae": 55.05500000000001, "bias": -72.73184782608696, "r2": 0.45833061658916197, "spearman": 0.8336555430023292}`
- turn_overview/original_examples: n=83, `{"mae": 237.14096385542166, "rmse": 562.487827768701, "medae": 34.47333333333336, "bias": -75.80859437751, "r2": 0.44717640124466296, "spearman": 0.8372957125520559}`
- turn_keywords/all: n=92, `{"mae": 253.74170289855073, "rmse": 566.0544808323758, "medae": 44.04666666666668, "bias": -75.22764492753625, "r2": 0.46705403126357725, "spearman": 0.8401693629480999}`
- turn_keywords/original_examples: n=83, `{"mae": 235.39807228915663, "rmse": 557.6929055107552, "medae": 24.5, "bias": -79.04200803212852, "r2": 0.45656130849957755, "spearman": 0.8441577777442157}`
- full/all: n=92, `{"mae": 298.4168356758453, "rmse": 669.9791661533297, "medae": 94.94917869070827, "bias": -220.3620133867866, "r2": 0.25339771923113497, "spearman": 0.7896328776733356}`
- full/original_examples: n=83, `{"mae": 287.456157812929, "rmse": 661.3139840899794, "medae": 91.415468648883, "bias": -217.30314592172587, "r2": 0.23585508229571428, "spearman": 0.7901845362354804}`

### remaining_turns

- turn/all: n=92, `{"mae": 0.004306785019646958, "rmse": 0.012556813496485936, "medae": 0.0018752001601380908, "bias": 0.0009771546882487677, "r2": 0.9993583898770527, "spearman": 0.8598844374277045}`
- turn/original_examples: n=83, `{"mae": 0.0031407715608986956, "rmse": 0.006251182057790661, "medae": 0.0016991054655953741, "bias": -0.0004423329418189499, "r2": 0.9998425711332881, "spearman": 0.8646557597139881}`
- turn_overview/all: n=92, `{"mae": 0.00474602228087397, "rmse": 0.012709465321688129, "medae": 0.002109568881481949, "bias": 0.0015644099278340508, "r2": 0.9993426950835713, "spearman": 0.8588629209148368}`
- turn_overview/original_examples: n=83, `{"mae": 0.0035791189662366077, "rmse": 0.006561982219604284, "medae": 0.001957783129791779, "bias": 0.00011143900012119521, "r2": 0.9998265276855143, "spearman": 0.86325633065631}`
- turn_keywords/all: n=92, `{"mae": 0.006573186231549057, "rmse": 0.019939822953184125, "medae": 0.002040966717872905, "bias": 0.0027345979809448233, "r2": 0.9983820879281162, "spearman": 0.8609362842275782}`
- turn_keywords/original_examples: n=83, `{"mae": 0.004035678218312024, "rmse": 0.009175572344221965, "medae": 0.0018963418873970683, "bias": 0.0004010852440313472, "r2": 0.9996608229943171, "spearman": 0.8660986344123205}`
- full/all: n=92, `{"mae": 0.007135534571488219, "rmse": 0.027113526817390488, "medae": 2.886579864025407e-15, "bias": -0.004483365302628542, "r2": 0.9970085321154114, "spearman": 0.9264995642908782}`
- full/original_examples: n=83, `{"mae": 0.006928799651642429, "rmse": 0.02820048201042727, "medae": 2.886579864025407e-15, "bias": -0.004838802964264893, "r2": 0.9967961428995677, "spearman": 0.9556349667156846}`

### wave2_cost

- turn/all: n=51, `{"mae": 460.38196078431366, "rmse": 764.9103198312295, "medae": 298.1533333333333, "bias": -120.27947712418302, "r2": 0.07771442111069082, "spearman": 0.24242012951128872}`
- turn/original_examples: n=44, `{"mae": 437.0045454545454, "rmse": 764.5581272942014, "medae": 271.90166666666664, "bias": -136.84242424242422, "r2": 0.06075256390455264, "spearman": 0.19431914486834237}`
- turn_overview/all: n=51, `{"mae": 453.6694020853501, "rmse": 806.4119048681443, "medae": 242.0766635054963, "bias": -202.85130621709837, "r2": -0.025081128827912913, "spearman": 0.23065435880512203}`
- turn_overview/original_examples: n=44, `{"mae": 443.0512275319513, "rmse": 818.6802664469619, "medae": 225.13489381357363, "bias": -208.95665456149106, "r2": -0.07693041896805108, "spearman": 0.1596419525305751}`
- turn_keywords/all: n=51, `{"mae": 466.5639689217585, "rmse": 807.4619185603472, "medae": 232.14584272276988, "bias": -203.13477357511906, "r2": -0.027752344273442642, "spearman": 0.2575346195722875}`
- turn_keywords/original_examples: n=44, `{"mae": 452.94724967910656, "rmse": 819.3359491456624, "medae": 212.95652934984548, "bias": -204.36095143983567, "r2": -0.07865614130608312, "spearman": 0.20157880098783432}`
- full/all: n=51, `{"mae": 529.0923504598971, "rmse": 867.4261256155288, "medae": 305.25544568682807, "bias": -340.64898036635486, "r2": -0.18606741342728594, "spearman": 0.12974024851761526}`
- full/original_examples: n=44, `{"mae": 528.4051137426327, "rmse": 885.3674484729592, "medae": 302.1172955360838, "bias": -365.287732601801, "r2": -0.2595229955279086, "spearman": 0.038694671937874486}`

### solvable

- turn/all: n=92, `{"accuracy": 0.6739130434782609, "balanced_accuracy": 0.34444444444444444, "brier": 0.21169685990338163, "log_loss": 0.6128019236267048, "base_rate": 0.9782608695652174, "roc_auc": 0.44999999999999996, "average_precision": 0.9797247342861404}`
- turn/original_examples: n=83, `{"accuracy": 0.6987951807228916, "balanced_accuracy": NaN, "brier": 0.1995606425702811, "log_loss": 0.5842658319233858, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn_overview/all: n=92, `{"accuracy": 0.532608695652174, "balanced_accuracy": 0.2722222222222222, "brier": 0.35459007614354027, "log_loss": 1.115328972194342, "base_rate": 0.9782608695652174, "roc_auc": 0.011111111111111112, "average_precision": 0.9283425023434234}`
- turn_overview/original_examples: n=83, `{"accuracy": 0.5662650602409639, "balanced_accuracy": NaN, "brier": 0.318024689447514, "log_loss": 0.9872275380316444, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- turn_keywords/all: n=92, `{"accuracy": 0.7065217391304348, "balanced_accuracy": 0.85, "brier": 0.25412638905532076, "log_loss": 0.7820410074292549, "base_rate": 0.9782608695652174, "roc_auc": 1.0, "average_precision": 0.9999999999999998}`
- turn_keywords/original_examples: n=83, `{"accuracy": 0.7108433734939759, "balanced_accuracy": NaN, "brier": 0.25231622817073546, "log_loss": 0.7772124527377161, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`
- full/all: n=92, `{"accuracy": 0.8152173913043478, "balanced_accuracy": 0.9055555555555556, "brier": 0.19369903381642514, "log_loss": 0.5760142639873201, "base_rate": 0.9782608695652174, "roc_auc": 0.9111111111111112, "average_precision": 0.9979880600129858}`
- full/original_examples: n=83, `{"accuracy": 0.8192771084337349, "balanced_accuracy": NaN, "brier": 0.1973534136546185, "log_loss": 0.5859205853338091, "base_rate": 1.0, "roc_auc": NaN, "average_precision": NaN}`

### wave2_any_answer

- turn/all: n=51, `{"accuracy": 0.5490196078431373, "balanced_accuracy": 0.6027777777777777, "brier": 0.27774772291286987, "log_loss": 0.7940908580116124, "base_rate": 0.7058823529411765, "roc_auc": 0.487037037037037, "average_precision": 0.693410024697126}`
- turn/original_examples: n=44, `{"accuracy": 0.5681818181818182, "balanced_accuracy": 0.6265508684863523, "brier": 0.26872997892623585, "log_loss": 0.7334086087054289, "base_rate": 0.7045454545454546, "roc_auc": 0.5012406947890818, "average_precision": 0.7070010773543876}`
- turn_overview/all: n=51, `{"accuracy": 0.5098039215686274, "balanced_accuracy": 0.5361111111111111, "brier": 0.35081465445257304, "log_loss": 1.3593049086414863, "base_rate": 0.7058823529411765, "roc_auc": 0.55, "average_precision": 0.7575343790390809}`
- turn_overview/original_examples: n=44, `{"accuracy": 0.5227272727272727, "balanced_accuracy": 0.5272952853598014, "brier": 0.33794219579335705, "log_loss": 1.1329902216648167, "base_rate": 0.7045454545454546, "roc_auc": 0.5235732009925558, "average_precision": 0.747630236520956}`
- turn_keywords/all: n=51, `{"accuracy": 0.49019607843137253, "balanced_accuracy": 0.5222222222222221, "brier": 0.2832583407867056, "log_loss": 0.7751217896711334, "base_rate": 0.7058823529411765, "roc_auc": 0.4462962962962963, "average_precision": 0.6700817699089228}`
- turn_keywords/original_examples: n=44, `{"accuracy": 0.5, "balanced_accuracy": 0.533498759305211, "brier": 0.27748962719884984, "log_loss": 0.7535432859074157, "base_rate": 0.7045454545454546, "roc_auc": 0.4540942928039702, "average_precision": 0.6777830891397}`
- full/all: n=51, `{"accuracy": 0.5294117647058824, "balanced_accuracy": 0.5888888888888888, "brier": 0.4139039258219255, "log_loss": 3.8300186523148825, "base_rate": 0.7058823529411765, "roc_auc": 0.6148148148148148, "average_precision": 0.7773304864300178}`
- full/original_examples: n=44, `{"accuracy": 0.5227272727272727, "balanced_accuracy": 0.5719602977667494, "brier": 0.41533457202595225, "log_loss": 4.188897335104252, "base_rate": 0.7045454545454546, "roc_auc": 0.6079404466501241, "average_precision": 0.7710135668074949}`

