# Experiment 0004: comparison

## Configurations (mean ± sd over runs)

| config | runs | score | solved | cost | wave1 cost | wave1 answered | wave2 cost | unanswered | wave2 attempted | wave2 solved | conversion |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| base-nn | 4 | 81.75 ± 3.70 | 19.25 ± 0.83 | 13117 ± 923 | 9622 | 20.8 | 3495 | 45 | 45 | 8 | 17.8% |
| goal-nn | 4 | 80.75 ± 6.72 | 18.50 ± 2.06 | 15946 ± 838 | 11286 | 18.2 | 4661 | 55 | 55 | 16 | 29.1% |

## First-turn data collection on unanswered tasks

| config | script chars | script lines | output chars | has head/tail | has cat | corr(output, wave2 success) | corr(lines, wave2 success) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| base-nn | 562 | 6.7 | 281 | 0.33 | 0.53 | -0.06 | -0.22 |
| goal-nn | 755 | 7.5 | 383 | 0.22 | 0.62 | -0.02 | -0.11 |

## Paired task comparison

`Δ` — средняя разница на задачу по повторам; `only left/right` — исходы по парам задача-повтор.

| left | right | runs | both | only left | only right | neither | McNemar p | Δ score (mean [95% CI]) | Δ cost (mean [95% CI]) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| base-nn | goal-nn | 4 | 68 | 9 | 6 | 45 | 0.6072 | +0.03 [-0.12, +0.19] | -88 [-159, -12] |

## By category (aggregated over runs)

### coding

| config | task-runs | solved | score | cost | wave1 answered | wave2 solved |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| base-nn | 32 | 18 | 99 | 10833 | 18 | 3 |
| goal-nn | 32 | 18 | 100 | 17967 | 13 | 9 |

### data_analysis

| config | task-runs | solved | score | cost | wave1 answered | wave2 solved |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| base-nn | 32 | 24 | 80 | 10495 | 31 | 0 |
| goal-nn | 32 | 24 | 80 | 12104 | 30 | 0 |

### math

| config | task-runs | solved | score | cost | wave1 answered | wave2 solved |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| base-nn | 32 | 24 | 116 | 15454 | 22 | 4 |
| goal-nn | 32 | 22 | 114 | 20007 | 21 | 4 |

### search

| config | task-runs | solved | score | cost | wave1 answered | wave2 solved |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| base-nn | 32 | 11 | 32 | 15687 | 12 | 1 |
| goal-nn | 32 | 10 | 29 | 13708 | 9 | 3 |


## Per run

| config | run | score | solved | cost | wave1 cost | wave1 answered | wave2 cost | duration s | rc |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| base-nn | 1 | 85 | 20 | 14551 | 10758 | 24 | 3793 | 205.0 | 0 |
| base-nn | 2 | 76 | 18 | 12758 | 9158 | 19 | 3600 | 285.6 | 0 |
| base-nn | 3 | 81 | 19 | 13149 | 9178 | 20 | 3971 | 240.6 | 0 |
| base-nn | 4 | 85 | 20 | 12011 | 9394 | 20 | 2617 | 175.8 | 0 |
| goal-nn | 1 | 73 | 16 | 14824 | 10379 | 17 | 4445 | 466.3 | 0 |
| goal-nn | 2 | 77 | 17 | 16020 | 11588 | 18 | 4432 | 213.1 | 0 |
| goal-nn | 3 | 91 | 21 | 17175 | 11476 | 18 | 5699 | 177.2 | 0 |
| goal-nn | 4 | 82 | 20 | 15767 | 11699 | 20 | 4068 | 196.4 | 0 |
