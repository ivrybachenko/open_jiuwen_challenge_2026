# Сравнение горизонтального и вертикального разбиений

## Состав разбиений

| Прогон | Режим | Задачи train/val/test | Типы |
| --- | --- | --- | --- |
| horizontal | horizontal | 136/45/59 | все категории |
| vertical-search | vertical | 120/60/60 | ['coding', 'data_analysis'] → math / search |
| vertical-coding | vertical | 120/60/60 | ['data_analysis', 'math'] → search / coding |
| vertical-data-analysis | vertical | 120/60/60 | ['math', 'search'] → coding / data_analysis |
| vertical-math | vertical | 120/60/60 | ['search', 'coding'] → data_analysis / math |

## solvable

ROC-AUC на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.804 | 0.645 | 0.560 | 0.677 | 0.837 |
| turn_overview | 0.738 | 0.643 | 0.625 | 0.744 | 0.807 |
| turn_keywords | 0.817 | 0.640 | 0.667 | 0.695 | 0.756 |
| full | 0.973 | 0.650 | 0.605 | 0.789 | 0.797 |

PR-AUC на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.909 | 0.747 | 0.732 | 0.809 | 0.923 |
| turn_overview | 0.887 | 0.746 | 0.786 | 0.872 | 0.917 |
| turn_keywords | 0.869 | 0.761 | 0.792 | 0.824 | 0.878 |
| full | 0.991 | 0.793 | 0.795 | 0.863 | 0.912 |

Brier на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.157 | 0.307 | 0.246 | 0.206 | 0.173 |
| turn_overview | 0.215 | 0.310 | 0.219 | 0.186 | 0.170 |
| turn_keywords | 0.163 | 0.302 | 0.212 | 0.203 | 0.186 |
| full | 0.078 | 0.281 | 0.279 | 0.210 | 0.259 |

Выбранные модели:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | --- | --- | --- | --- | --- |
| turn | random_forest | logistic_regression | random_forest | random_forest | random_forest |
| turn_overview | hist_gradient_boosting | logistic_regression | random_forest | random_forest | random_forest |
| turn_keywords | logistic_regression | logistic_regression | random_forest | random_forest | random_forest |
| full | random_forest | logistic_regression | random_forest | logistic_regression | hist_gradient_boosting |

## solved_correctly

ROC-AUC на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.798 | 0.671 | 0.655 | 0.823 | 0.682 |
| turn_overview | 0.761 | 0.710 | 0.588 | 0.611 | 0.744 |
| turn_keywords | 0.838 | 0.724 | 0.638 | 0.796 | 0.628 |
| full | 0.861 | 0.604 | 0.604 | 0.826 | 0.784 |

PR-AUC на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.831 | 0.551 | 0.667 | 0.824 | 0.796 |
| turn_overview | 0.778 | 0.594 | 0.663 | 0.683 | 0.853 |
| turn_keywords | 0.886 | 0.662 | 0.624 | 0.811 | 0.743 |
| full | 0.867 | 0.619 | 0.704 | 0.901 | 0.854 |

Brier на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.179 | 0.251 | 0.262 | 0.169 | 0.218 |
| turn_overview | 0.215 | 0.238 | 0.287 | 0.276 | 0.212 |
| turn_keywords | 0.160 | 0.243 | 0.252 | 0.178 | 0.223 |
| full | 0.155 | 0.299 | 0.253 | 0.205 | 0.191 |

Выбранные модели:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | --- | --- | --- | --- | --- |
| turn | random_forest | logistic_regression | random_forest | random_forest | random_forest |
| turn_overview | logistic_regression | logistic_regression | random_forest | logistic_regression | hist_gradient_boosting |
| turn_keywords | random_forest | logistic_regression | random_forest | random_forest | random_forest |
| full | random_forest | logistic_regression | random_forest | hist_gradient_boosting | random_forest |

## wave2_any_answer

ROC-AUC на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.229 | 0.524 | 0.524 | 0.384 | 0.778 |
| turn_overview | 0.167 | 0.538 | 0.545 | 0.375 | 0.889 |
| turn_keywords | 0.236 | 0.524 | 0.545 | 0.464 | 0.778 |
| full | 0.417 | 0.608 | 0.530 | 0.446 | 0.556 |

PR-AUC на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.549 | 0.628 | 0.654 | 0.632 | 0.977 |
| turn_overview | 0.492 | 0.635 | 0.647 | 0.642 | 0.989 |
| turn_keywords | 0.535 | 0.592 | 0.667 | 0.676 | 0.977 |
| full | 0.642 | 0.746 | 0.680 | 0.679 | 0.947 |

Brier на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.303 | 0.284 | 0.300 | 0.364 | 0.188 |
| turn_overview | 0.576 | 0.276 | 0.285 | 0.440 | 0.186 |
| turn_keywords | 0.288 | 0.282 | 0.275 | 0.387 | 0.188 |
| full | 0.335 | 0.293 | 0.256 | 0.414 | 0.188 |

Выбранные модели:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | --- | --- | --- | --- | --- |
| turn | logistic_regression | logistic_regression | random_forest | logistic_regression | hist_gradient_boosting |
| turn_overview | logistic_regression | logistic_regression | random_forest | logistic_regression | random_forest |
| turn_keywords | logistic_regression | logistic_regression | random_forest | logistic_regression | hist_gradient_boosting |
| full | logistic_regression | logistic_regression | random_forest | logistic_regression | random_forest |

## wave2_success

ROC-AUC на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.682 | 0.600 | 0.751 | 0.733 | 0.720 |
| turn_overview | 0.494 | 0.589 | 0.792 | 0.724 | 0.720 |
| turn_keywords | 0.688 | 0.653 | 0.749 | 0.724 | 0.680 |
| full | 0.773 | 0.379 | 0.683 | 0.667 | 0.520 |

PR-AUC на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.725 | 0.329 | 0.602 | 0.677 | 0.833 |
| turn_overview | 0.574 | 0.325 | 0.714 | 0.621 | 0.810 |
| turn_keywords | 0.721 | 0.485 | 0.567 | 0.584 | 0.814 |
| full | 0.799 | 0.385 | 0.560 | 0.648 | 0.672 |

Brier на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.221 | 0.199 | 0.194 | 0.229 | 0.195 |
| turn_overview | 0.325 | 0.188 | 0.181 | 0.204 | 0.214 |
| turn_keywords | 0.220 | 0.209 | 0.196 | 0.239 | 0.206 |
| full | 0.190 | 0.238 | 0.236 | 0.196 | 0.241 |

Выбранные модели:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | --- | --- | --- | --- | --- |
| turn | random_forest | logistic_regression | random_forest | random_forest | random_forest |
| turn_overview | logistic_regression | logistic_regression | random_forest | random_forest | random_forest |
| turn_keywords | random_forest | logistic_regression | random_forest | random_forest | random_forest |
| full | random_forest | logistic_regression | random_forest | random_forest | random_forest |

## remaining_tokens

MAE на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 194.908 | 267.578 | 501.474 | 113.927 | 106.306 |
| turn_overview | 195.063 | 262.315 | 511.341 | 112.382 | 93.230 |
| turn_keywords | 191.033 | 257.125 | 492.224 | 126.662 | 96.623 |
| full | 158.930 | 272.248 | 584.338 | 102.178 | 176.048 |

Spearman на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.860 | 0.772 | 0.577 | 0.826 | 0.941 |
| turn_overview | 0.853 | 0.770 | 0.622 | 0.827 | 0.853 |
| turn_keywords | 0.857 | 0.769 | 0.711 | 0.818 | 0.859 |
| full | 0.850 | 0.753 | 0.122 | 0.894 | 0.869 |

R² на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.415 | 0.373 | 0.092 | 0.607 | 0.745 |
| turn_overview | 0.414 | 0.364 | 0.031 | 0.620 | 0.749 |
| turn_keywords | 0.427 | 0.373 | 0.097 | 0.562 | 0.764 |
| full | 0.427 | 0.385 | -0.003 | 0.673 | 0.333 |

Выбранные модели:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | --- | --- | --- | --- | --- |
| turn | random_forest | random_forest | random_forest_log | random_forest_log | random_forest |
| turn_overview | random_forest | random_forest | random_forest_log | random_forest_log | random_forest |
| turn_keywords | random_forest | random_forest | random_forest_log | random_forest_log | random_forest |
| full | random_forest_log | random_forest | hist_gradient_boosting_log | random_forest_log | random_forest_log |

## remaining_turns

MAE на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.006 | 0.061 | 0.250 | 0.057 | 0.028 |
| turn_overview | 0.006 | 0.061 | 0.250 | 0.058 | 0.051 |
| turn_keywords | 0.008 | 0.063 | 0.250 | 0.069 | 0.062 |
| full | 0.012 | 0.041 | 0.250 | 0.002 | 0.064 |

Spearman на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.868 | 0.872 | 0.295 | 0.842 | 0.858 |
| turn_overview | 0.868 | 0.872 | 0.295 | 0.842 | 0.946 |
| turn_keywords | 0.869 | 0.863 | 0.295 | 0.842 | 0.942 |
| full | 0.911 | 0.866 | 0.295 | 0.987 | 0.944 |

R² на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.999 | 0.782 | -0.231 | 0.978 | 0.956 |
| turn_overview | 0.999 | 0.782 | -0.231 | 0.979 | 0.952 |
| turn_keywords | 0.999 | 0.784 | -0.231 | 0.971 | 0.926 |
| full | 0.996 | 0.957 | -0.231 | 0.999 | 0.920 |

Выбранные модели:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | --- | --- | --- | --- | --- |
| turn | ridge | ridge | hist_gradient_boosting | ridge | ridge |
| turn_overview | ridge | ridge | hist_gradient_boosting | ridge | random_forest |
| turn_keywords | ridge | ridge | hist_gradient_boosting | ridge | random_forest |
| full | random_forest_log | random_forest | hist_gradient_boosting | random_forest_log | random_forest |

## wave2_cost

MAE на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 440.208 | 395.128 | 529.542 | 270.191 | 227.810 |
| turn_overview | 303.314 | 395.813 | 589.026 | 268.623 | 231.733 |
| turn_keywords | 295.589 | 397.059 | 530.302 | 272.940 | 217.443 |
| full | 324.164 | 391.669 | 544.373 | 287.759 | 301.337 |

Spearman на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.182 | 0.439 | 0.175 | 0.011 | 0.224 |
| turn_overview | 0.555 | 0.437 | 0.389 | 0.077 | 0.321 |
| turn_keywords | 0.518 | 0.430 | 0.151 | -0.025 | 0.212 |
| full | 0.319 | 0.463 | 0.332 | 0.076 | 0.261 |

R² на test:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | -0.277 | 0.001 | -0.071 | -0.072 | -2.669 |
| turn_overview | -0.004 | 0.008 | -0.321 | -0.059 | -2.812 |
| turn_keywords | -0.007 | -0.013 | -0.072 | -0.079 | -2.203 |
| full | -0.064 | 0.008 | -0.165 | -0.065 | -5.281 |

Выбранные модели:

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | --- | --- | --- | --- | --- |
| turn | random_forest | random_forest_log | random_forest | random_forest | random_forest_log |
| turn_overview | ridge | random_forest_log | random_forest_log | random_forest | random_forest_log |
| turn_keywords | ridge | random_forest_log | random_forest | random_forest | random_forest_log |
| full | ridge | random_forest_log | random_forest_log | random_forest | random_forest_log |

## Сводка: горизонтальное vs вертикальные разбиения

Для вертикальных разбиений показаны среднее и диапазон по ротациям. Δ — среднее вертикальное минус горизонтальное; для ROC-AUC положительная Δ означает лучше, для MAE — хуже.

### solvable, ROC-AUC

| Набор признаков | Горизонт. | Вертик. среднее | Вертик. диапазон | Δ |
| --- | ---: | ---: | --- | ---: |
| turn | 0.804 | 0.680 | 0.560–0.837 | -0.124 |
| turn_overview | 0.738 | 0.705 | 0.625–0.807 | -0.033 |
| turn_keywords | 0.817 | 0.690 | 0.640–0.756 | -0.127 |
| full | 0.973 | 0.710 | 0.605–0.797 | -0.263 |

### solved_correctly, ROC-AUC

| Набор признаков | Горизонт. | Вертик. среднее | Вертик. диапазон | Δ |
| --- | ---: | ---: | --- | ---: |
| turn | 0.798 | 0.708 | 0.655–0.823 | -0.090 |
| turn_overview | 0.761 | 0.663 | 0.588–0.744 | -0.097 |
| turn_keywords | 0.838 | 0.697 | 0.628–0.796 | -0.141 |
| full | 0.861 | 0.705 | 0.604–0.826 | -0.157 |

### wave2_any_answer, ROC-AUC

| Набор признаков | Горизонт. | Вертик. среднее | Вертик. диапазон | Δ |
| --- | ---: | ---: | --- | ---: |
| turn | 0.229 | 0.553 | 0.384–0.778 | 0.323 |
| turn_overview | 0.167 | 0.587 | 0.375–0.889 | 0.420 |
| turn_keywords | 0.236 | 0.578 | 0.464–0.778 | 0.342 |
| full | 0.417 | 0.535 | 0.446–0.608 | 0.118 |

### wave2_success, ROC-AUC

| Набор признаков | Горизонт. | Вертик. среднее | Вертик. диапазон | Δ |
| --- | ---: | ---: | --- | ---: |
| turn | 0.682 | 0.701 | 0.600–0.751 | 0.019 |
| turn_overview | 0.494 | 0.706 | 0.589–0.792 | 0.213 |
| turn_keywords | 0.688 | 0.701 | 0.653–0.749 | 0.013 |
| full | 0.773 | 0.562 | 0.379–0.683 | -0.211 |

### remaining_tokens, MAE (меньше лучше)

| Набор признаков | Горизонт. | Вертик. среднее | Вертик. диапазон | Δ |
| --- | ---: | ---: | --- | ---: |
| turn | 194.908 | 247.321 | 106.306–501.474 | 52.414 |
| turn_overview | 195.063 | 244.817 | 93.230–511.341 | 49.754 |
| turn_keywords | 191.033 | 243.159 | 96.623–492.224 | 52.126 |
| full | 158.930 | 283.703 | 102.178–584.338 | 124.773 |

### remaining_turns, MAE (меньше лучше)

| Набор признаков | Горизонт. | Вертик. среднее | Вертик. диапазон | Δ |
| --- | ---: | ---: | --- | ---: |
| turn | 0.006 | 0.099 | 0.028–0.250 | 0.094 |
| turn_overview | 0.006 | 0.105 | 0.051–0.250 | 0.099 |
| turn_keywords | 0.008 | 0.111 | 0.062–0.250 | 0.103 |
| full | 0.012 | 0.089 | 0.002–0.250 | 0.077 |

### wave2_cost, MAE (меньше лучше)

| Набор признаков | Горизонт. | Вертик. среднее | Вертик. диапазон | Δ |
| --- | ---: | ---: | --- | ---: |
| turn | 440.208 | 355.668 | 227.810–529.542 | -84.540 |
| turn_overview | 303.314 | 371.299 | 231.733–589.026 | 67.984 |
| turn_keywords | 295.589 | 354.436 | 217.443–530.302 | 58.847 |
| full | 324.164 | 381.285 | 287.759–544.373 | 57.121 |

## Гипотеза о ключевых словах

Разница `turn_keywords - turn` на test. Для классификации — ROC-AUC (больше лучше), для регрессии — MAE (меньше лучше).

| Цель | Метрика | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| solvable | Δ ROC-AUC | 0.013 | -0.005 | 0.107 | 0.017 | -0.081 |
| solved_correctly | Δ ROC-AUC | 0.040 | 0.053 | -0.017 | -0.027 | -0.054 |
| wave2_any_answer | Δ ROC-AUC | 0.007 | -0.000 | 0.021 | 0.080 | 0.000 |
| wave2_success | Δ ROC-AUC | 0.006 | 0.053 | -0.002 | -0.010 | -0.040 |
| remaining_tokens | Δ MAE | -3.875 | -10.452 | -9.249 | 12.735 | -9.683 |
| remaining_turns | Δ MAE | 0.002 | 0.002 | 0.000 | 0.012 | 0.034 |
| wave2_cost | Δ MAE | -144.619 | 1.931 | 0.760 | 2.748 | -10.367 |

## Статические признаки и переобучение

Разница `full - turn_overview` на test. Если она положительна, статические признаки задачи помогают; если исчезает на вертикальном разбиении — модель опирается на особенности категорий/генератора.

| Цель | Метрика | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| solvable | Δ ROC-AUC | 0.235 | 0.007 | -0.020 | 0.045 | -0.010 |
| solved_correctly | Δ ROC-AUC | 0.101 | -0.106 | 0.016 | 0.215 | 0.040 |
| wave2_any_answer | Δ ROC-AUC | 0.250 | 0.070 | -0.015 | 0.071 | -0.333 |
| wave2_success | Δ ROC-AUC | 0.279 | -0.211 | -0.109 | -0.057 | -0.200 |
| remaining_tokens | Δ MAE | -36.133 | 9.932 | 72.996 | -10.204 | 82.818 |
| remaining_turns | Δ MAE | 0.007 | -0.021 | 0.000 | -0.056 | 0.014 |
| wave2_cost | Δ MAE | 20.850 | -4.144 | -44.652 | 19.136 | 69.604 |

## Внешняя проверка на других прогонах

### solvable, ROC-AUC

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.450 | — | — | — | 0.200 |
| turn_overview | 0.011 | — | — | — | 0.000 |
| turn_keywords | 1.000 | — | — | — | 0.325 |
| full | 0.911 | — | — | — | 0.000 |

### wave2_any_answer, ROC-AUC

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.487 | 0.407 | 0.333 | 0.667 | 1.000 |
| turn_overview | 0.550 | 0.364 | 0.373 | 0.667 | 0.500 |
| turn_keywords | 0.446 | 0.379 | 0.324 | 0.333 | 1.000 |
| full | 0.615 | 0.400 | 0.216 | 0.000 | 0.000 |

### wave2_success, ROC-AUC

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | — | — | — | — | — |
| turn_overview | — | — | — | — | — |
| turn_keywords | — | — | — | — | — |
| full | — | — | — | — | — |

### remaining_tokens, MAE

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 257.514 | 724.606 | 395.907 | 36.599 | 109.361 |
| turn_overview | 255.232 | 729.267 | 437.156 | 35.726 | 115.230 |
| turn_keywords | 253.742 | 728.267 | 388.378 | 28.330 | 112.524 |
| full | 298.417 | 757.465 | 305.937 | 69.999 | 35.730 |

### remaining_turns, MAE

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 0.004 | 0.002 | 0.045 | 0.058 | 0.016 |
| turn_overview | 0.005 | 0.002 | 0.045 | 0.070 | 0.022 |
| turn_keywords | 0.007 | 0.004 | 0.045 | 0.064 | 0.018 |
| full | 0.007 | 0.023 | 0.045 | 0.000 | 0.017 |

### wave2_cost, MAE

| Набор признаков | horizontal | vertical-search | vertical-coding | vertical-data-analysis | vertical-math |
| --- | ---: | ---: | ---: | ---: | ---: |
| turn | 460.382 | 672.815 | 227.060 | 400.767 | 247.795 |
| turn_overview | 453.669 | 669.659 | 451.074 | 425.479 | 240.565 |
| turn_keywords | 466.564 | 674.600 | 224.071 | 396.159 | 245.559 |
| full | 529.092 | 674.936 | 362.462 | 440.345 | 298.381 |

