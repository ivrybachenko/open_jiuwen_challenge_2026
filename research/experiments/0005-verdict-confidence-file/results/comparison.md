# Experiment 0005: comparison

## Configurations (mean ± sd over runs)

| config | runs | score | solved | cost | wave1 cost | verdict turns | valid verdicts | missing | malformed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| base-nn | 2 | 79.50 ± 0.50 | 17.50 | 14270 ± 828 | 9820 | - | - | - | - |
| verdict-hard-nn | 4 | 79.25 ± 4.71 | 18.00 | 19443 ± 3041 | 12549 | 256 | 116 (45.3%) | 139 | 1 |
| verdict-nn | 2 | 85.50 ± 6.50 | 20.00 | 14693 ± 5 | 10216 | 128 | 15 (11.7%) | 113 | 0 |

## Verdict accuracy and calibration (final turn)

| config | n | coverage | accuracy | mean confidence | Brier | Brier constant | ECE | AUC (solved → correct) | solved precision | impossible recall | false impossible | reward lost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| base-nn | 0 | 0.0 | - | - | - | - | - | - | - | - | 0 | 0 |
| verdict-hard-nn | 106 | 0.8 | 0.651 | 0.985 | 0.333 | 0.227 | 0.334 | 0.514 | 0.654 | 0.043 | 0 | 0 |
| verdict-nn | 11 | 0.2 | 0.636 | 0.864 | 0.386 | 0.231 | 0.409 | 0.625 | 0.600 | 0.250 | 0 | 0 |

## Per-wave calibration

| config | wave | n | accuracy | mean confidence | Brier | ECE |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| verdict-hard-nn | wave1 | 91 | 0.725 | 0.989 | 0.264 | 0.264 |
| verdict-hard-nn | wave2 | 25 | 0.280 | 0.978 | 0.690 | 0.698 |
| verdict-hard-nn | final | 106 | 0.651 | 0.985 | 0.333 | 0.334 |
| verdict-nn | wave1 | 10 | 0.700 | 1.000 | 0.300 | 0.300 |
| verdict-nn | wave2 | 5 | 0.200 | 0.700 | 0.850 | 0.900 |
| verdict-nn | final | 11 | 0.636 | 0.864 | 0.386 | 0.409 |

## Confusion matrix (final turn)

### base-nn

| expected \ verdict | solved | not_solved | impossible |
| --- | ---: | ---: | ---: |
| solved | 0 | 0 | 0 |
| not_solved | 0 | 0 | 0 |
| impossible | 0 | 0 | 0 |

### verdict-hard-nn

| expected \ verdict | solved | not_solved | impossible |
| --- | ---: | ---: | ---: |
| solved | 68 | 0 | 0 |
| not_solved | 15 | 0 | 0 |
| impossible | 21 | 1 | 1 |

### verdict-nn

| expected \ verdict | solved | not_solved | impossible |
| --- | ---: | ---: | ---: |
| solved | 6 | 0 | 0 |
| not_solved | 1 | 0 | 0 |
| impossible | 3 | 0 | 1 |

## Confidence buckets (final turn)

| config | bucket | n | accuracy | mean confidence |
| --- | --- | ---: | ---: | ---: |

| verdict-hard-nn | <0.50 | 1 | 0.000 | 0.000 |
| verdict-hard-nn | 0.50-0.80 | 1 | 0.000 | 0.500 |
| verdict-hard-nn | >=0.80 | 104 | 0.663 | 1.000 |

| verdict-nn | <0.50 | 1 | 1.000 | 0.000 |
| verdict-nn | 0.50-0.80 | 1 | 0.000 | 0.500 |
| verdict-nn | >=0.80 | 9 | 0.667 | 1.000 |

## Paired cost and score

| left | right | runs | both | only left | only right | neither | McNemar p | Δ score (mean [95% CI]) | Δ cost (mean [95% CI]) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| base-nn | verdict-nn | 2 | 34 | 1 | 6 | 23 | 0.1250 | -0.19 [-0.42, +0.03] | -13 [-110, +94] |
| base-nn | verdict-hard-nn | 2 | 31 | 4 | 5 | 24 | 1.0000 | +0.03 [-0.19, +0.28] | -174 [-383, -29] |

## Per run

| config | run | score | solved | cost | wave1 cost | verdict tasks | duration s | rc |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| base-nn | 1 | 79 | 17 | 15098 | 10013 | 0 | 151.8 | 0 |
| base-nn | 2 | 80 | 18 | 13443 | 9627 | 0 | 148.8 | 0 |
| verdict-hard-nn | 1 | 85 | 20 | 16277 | 11997 | 29 | 179.7 | 0 |
| verdict-hard-nn | 2 | 72 | 16 | 23378 | 12468 | 26 | 243.9 | 0 |
| verdict-hard-nn | 3 | 79 | 18 | 21423 | 13434 | 26 | 341.2 | 0 |
| verdict-hard-nn | 4 | 81 | 18 | 16694 | 12297 | 27 | 163.6 | 0 |
| verdict-nn | 1 | 79 | 18 | 14698 | 10170 | 6 | 154.3 | 0 |
| verdict-nn | 2 | 92 | 22 | 14688 | 10262 | 5 | 134.1 | 0 |
