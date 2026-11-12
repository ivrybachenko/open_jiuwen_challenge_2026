# Experiment 0003: comparison

> `max_score` в `summary.json` включает reward нерешаемых задач; реально достижимый максимум — 97 по решаемым задачам.

## Configurations

| config | wave1 | wave2 | explain | score | solved | cost | cost/solved | score/1k tok | wave1 cost | wave1 answered | wave2 cost | wave2 answered |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| nn-explain | qwen3.6-35b-a3b | qwen3.6-35b-a3b | allowed | 81 | 18/32 | 18231 | 1013 | 4.44 | 12003 | 23 | 6228 | 5 |
| nn-explain-single | qwen3.6-35b-a3b | qwen3.6-35b-a3b | single | 89 | 21/32 | 17493 | 833 | 5.09 | 12570 | 22 | 4923 | 5 |
| nn-plain | qwen3.6-35b-a3b | qwen3.6-35b-a3b | off | 78 | 17/32 | 12894 | 758 | 6.05 | 9204 | 19 | 3690 | 5 |
| nn-single | qwen3.6-35b-a3b | qwen3.6-35b-a3b | single-only | 91 | 22/32 | 14544 | 661 | 6.26 | 10875 | 23 | 3669 | 6 |
| nr-explain | qwen3.6-35b-a3b | qwen3.6-35b-a3b | allowed | 75 | 18/32 | 18981 | 1054 | 3.95 | 10482 | 21 | 8499 | 6 |
| nr-explain-single | qwen3.6-35b-a3b | qwen3.6-35b-a3b | single | 81 | 19/32 | 21371 | 1125 | 3.79 | 12139 | 22 | 9232 | 4 |
| nr-plain | qwen3.6-35b-a3b | qwen3.6-35b-a3b | off | 85 | 20/32 | 19506 | 975 | 4.36 | 8778 | 21 | 10728 | 4 |
| route-search-r | qwen3.6-35b-a3b | qwen3.6-35b-a3b | off | 80 | 19/32 | 24108 | 1269 | 3.32 | 13879 | 20 | 10229 | 5 |
| rr-explain | qwen3.6-35b-a3b | qwen3.6-35b-a3b | allowed | 88 | 20/32 | 40485 | 2024 | 2.17 | 22270 | 17 | 18215 | 8 |
| rr-explain-single | qwen3.6-35b-a3b | qwen3.6-35b-a3b | single | 87 | 21/32 | 33331 | 1587 | 2.61 | 19548 | 20 | 13783 | 6 |
| rr-plain | qwen3.6-35b-a3b | qwen3.6-35b-a3b | off | 90 | 22/32 | 36252 | 1648 | 2.48 | 19217 | 17 | 17035 | 7 |

## Wave behaviour

| config | wave1 hit limit | wave1 reasoning tok | wave1 w/ explanation | wave2 tasks | wave2 reasoning tok | wave2 w/ explanation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| nn-explain | 2 | 0 | 9 | 9 | 0 | 3 |
| nn-explain-single | 2 | 0 | 8 | 10 | 0 | 6 |
| nn-plain | 2 | 0 | 2 | 13 | 0 | 0 |
| nn-single | 2 | 0 | 1 | 9 | 0 | 0 |
| nr-explain | 1 | 0 | 9 | 11 | 0 | 1 |
| nr-explain-single | 1 | 0 | 8 | 10 | 0 | 1 |
| nr-plain | 1 | 0 | 2 | 11 | 0 | 2 |
| route-search-r | 2 | 0 | 0 | 12 | 0 | 1 |
| rr-explain | 3 | 0 | 3 | 15 | 0 | 2 |
| rr-explain-single | 4 | 0 | 2 | 12 | 0 | 2 |
| rr-plain | 1 | 0 | 2 | 15 | 0 | 2 |

## Reply format

`multi-block` — ответ содержал больше одного fenced-блока; `short script` — исполняемый скрипт короче 40 символов при длинном ответе; `echo DONE` — скрипт состоял только из записи DONE.

| config | wave | turns | with explanation | median blocks | single block | multi-block | short script | echo DONE only |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| nn-explain | 1 | 32 | 9 | 1 | 28 | 4 | 2 | 2 |
| nn-explain | 2 | 9 | 3 | 1 | 8 | 1 | 0 | 0 |
| nn-explain-single | 1 | 32 | 8 | 1 | 25 | 4 | 1 | 0 |
| nn-explain-single | 2 | 10 | 6 | 1 | 9 | 0 | 0 | 0 |
| nn-plain | 1 | 32 | 2 | 1 | 25 | 1 | 0 | 0 |
| nn-plain | 2 | 13 | 0 | 1 | 9 | 0 | 0 | 0 |
| nn-single | 1 | 32 | 1 | 1 | 29 | 1 | 0 | 0 |
| nn-single | 2 | 9 | 0 | 1 | 7 | 1 | 1 | 1 |
| nr-explain | 1 | 32 | 9 | 1 | 27 | 4 | 3 | 3 |
| nr-explain | 2 | 11 | 1 | 1 | 10 | 0 | 0 | 0 |
| nr-explain-single | 1 | 32 | 8 | 1 | 26 | 4 | 2 | 1 |
| nr-explain-single | 2 | 10 | 1 | 1 | 9 | 1 | 0 | 0 |
| nr-plain | 1 | 32 | 2 | 1 | 28 | 1 | 0 | 0 |
| nr-plain | 2 | 11 | 2 | 1 | 10 | 1 | 0 | 0 |
| route-search-r | 1 | 32 | 0 | 1 | 26 | 0 | 0 | 0 |
| route-search-r | 2 | 12 | 1 | 1 | 11 | 1 | 0 | 0 |
| rr-explain | 1 | 32 | 3 | 1 | 30 | 0 | 1 | 0 |
| rr-explain | 2 | 15 | 2 | 1 | 13 | 2 | 0 | 0 |
| rr-explain-single | 1 | 32 | 2 | 1 | 28 | 1 | 0 | 0 |
| rr-explain-single | 2 | 12 | 2 | 1 | 11 | 1 | 0 | 0 |
| rr-plain | 1 | 32 | 2 | 1 | 26 | 0 | 0 | 0 |
| rr-plain | 2 | 15 | 2 | 1 | 13 | 2 | 0 | 0 |

## Paired task comparison

`only left` — задача решена только в левом конфиге, `only right` — только в правом; `cost` — суммарная стоимость общих задач.

| left | right | tasks | both | only left | only right | neither | McNemar p | Δ score (mean [95% CI]) | Δ cost (mean [95% CI]) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| rr-plain | nr-plain | 32 | 20 | 2 | 0 | 10 | 0.5000 | +0.16 [+0.00, +0.41] | +523 [+358, +707] |
| nr-plain | nn-plain | 32 | 16 | 4 | 1 | 11 | 0.3750 | +0.22 [-0.16, +0.62] | +207 [+16, +479] |
| rr-plain | rr-explain | 32 | 19 | 3 | 1 | 9 | 0.6250 | +0.06 [-0.22, +0.31] | -132 [-511, +254] |
| nr-plain | nr-explain | 32 | 16 | 4 | 2 | 10 | 0.6875 | +0.31 [-0.28, +0.97] | +16 [-193, +301] |
| nn-plain | nn-explain | 32 | 15 | 2 | 3 | 12 | 1.0000 | -0.09 [-0.50, +0.28] | -167 [-381, -25] |
| rr-explain | nr-explain | 32 | 16 | 4 | 2 | 10 | 0.6875 | +0.41 [-0.06, +1.03] | +672 [+389, +1026] |
| nn-explain | nr-explain | 32 | 16 | 2 | 2 | 12 | 1.0000 | +0.19 [-0.28, +0.84] | -23 [-151, +151] |
| rr-plain | nn-plain | 32 | 17 | 5 | 0 | 10 | 0.0625 | +0.38 [+0.06, +0.75] | +730 [+472, +1058] |
| rr-plain | rr-explain-single | 32 | 21 | 1 | 0 | 10 | 1.0000 | +0.09 [+0.00, +0.28] | +91 [-293, +468] |
| nr-plain | nr-explain-single | 32 | 18 | 2 | 1 | 11 | 1.0000 | +0.12 [-0.22, +0.59] | -58 [-311, +244] |
| nn-plain | nn-explain-single | 32 | 17 | 0 | 4 | 11 | 0.1250 | -0.34 [-0.72, -0.03] | -144 [-253, -50] |
| rr-explain | rr-explain-single | 32 | 18 | 2 | 3 | 9 | 1.0000 | +0.03 [-0.28, +0.38] | +224 [+12, +461] |
| nr-explain | nr-explain-single | 32 | 15 | 3 | 4 | 10 | 1.0000 | -0.19 [-0.88, +0.50] | -75 [-216, +49] |
| rr-explain-single | nr-explain-single | 32 | 18 | 3 | 1 | 10 | 0.6250 | +0.19 [-0.19, +0.66] | +374 [+120, +682] |
| nr-explain-single | nn-explain-single | 32 | 18 | 1 | 3 | 10 | 0.6250 | -0.25 [-0.75, +0.09] | +121 [-20, +312] |
| rr-plain | route-search-r | 32 | 19 | 3 | 0 | 10 | 0.2500 | +0.31 [+0.00, +0.69] | +380 [+11, +723] |
| nr-plain | route-search-r | 32 | 17 | 3 | 2 | 10 | 1.0000 | +0.16 [-0.25, +0.59] | -144 [-513, +155] |
| route-search-r | nn-plain | 32 | 16 | 3 | 1 | 12 | 0.6250 | +0.06 [-0.22, +0.31] | +350 [+151, +644] |
| rr-plain | nn-explain-single | 32 | 20 | 2 | 1 | 9 | 1.0000 | +0.03 [-0.22, +0.25] | +586 [+324, +895] |
| nr-plain | nn-explain-single | 32 | 19 | 1 | 2 | 10 | 1.0000 | -0.12 [-0.47, +0.12] | +63 [-119, +325] |
| rr-plain | nr-explain-single | 32 | 19 | 3 | 0 | 10 | 0.2500 | +0.28 [+0.00, +0.72] | +465 [+165, +816] |
| rr-explain-single | nn-explain-single | 32 | 19 | 2 | 2 | 9 | 1.0000 | -0.06 [-0.41, +0.22] | +495 [+262, +769] |
| nn-explain-single | route-search-r | 32 | 17 | 4 | 2 | 9 | 0.6875 | +0.28 [-0.12, +0.75] | -207 [-506, -10] |
| nn-plain | nn-single | 32 | 17 | 0 | 5 | 10 | 0.0625 | -0.41 [-0.78, -0.09] | -52 [-161, +42] |
| nn-single | nn-explain-single | 32 | 20 | 2 | 1 | 9 | 1.0000 | +0.06 [-0.31, +0.44] | -92 [-241, +61] |
| nr-plain | nn-single | 32 | 19 | 1 | 3 | 9 | 0.6250 | -0.19 [-0.62, +0.25] | +155 [-58, +456] |
| rr-plain | nn-single | 32 | 20 | 2 | 2 | 8 | 1.0000 | -0.03 [-0.44, +0.38] | +678 [+408, +1028] |

## By solvability

| config | group | tasks | solved | score | cost | wave1 answered | wave1 closed | wave2 closed | wave1 cost | wave2 cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| nn-explain | solvable | 24 | 18 | 81 | 9507 | 21 | 16 | 2 | 8576 | 931 |
| nn-explain | impossible | 8 | 0 | 0 | 8724 | 2 | 0 | 0 | 3427 | 5297 |
| nn-explain-single | solvable | 24 | 21 | 89 | 11300 | 20 | 20 | 1 | 9254 | 2046 |
| nn-explain-single | impossible | 8 | 0 | 0 | 6193 | 2 | 0 | 0 | 3316 | 2877 |
| nn-plain | solvable | 24 | 17 | 78 | 7555 | 17 | 15 | 2 | 6092 | 1463 |
| nn-plain | impossible | 8 | 0 | 0 | 5339 | 2 | 0 | 0 | 3112 | 2227 |
| nn-single | solvable | 24 | 22 | 91 | 7955 | 19 | 18 | 4 | 6763 | 1192 |
| nn-single | impossible | 8 | 0 | 0 | 6589 | 4 | 0 | 0 | 4112 | 2477 |
| nr-explain | solvable | 24 | 18 | 75 | 11004 | 18 | 15 | 3 | 7326 | 3678 |
| nr-explain | impossible | 8 | 0 | 0 | 7977 | 3 | 0 | 0 | 3156 | 4821 |
| nr-explain-single | solvable | 24 | 19 | 81 | 12070 | 20 | 17 | 2 | 9145 | 2925 |
| nr-explain-single | impossible | 8 | 0 | 0 | 9301 | 2 | 0 | 0 | 2994 | 6307 |
| nr-plain | solvable | 24 | 20 | 85 | 11133 | 18 | 18 | 2 | 5905 | 5228 |
| nr-plain | impossible | 8 | 0 | 0 | 8373 | 3 | 0 | 0 | 2873 | 5500 |
| route-search-r | solvable | 24 | 19 | 80 | 17305 | 17 | 16 | 3 | 9602 | 7703 |
| route-search-r | impossible | 8 | 0 | 0 | 6803 | 3 | 0 | 0 | 4277 | 2526 |
| rr-explain | solvable | 24 | 20 | 88 | 30684 | 15 | 14 | 6 | 17416 | 13268 |
| rr-explain | impossible | 8 | 0 | 0 | 9801 | 2 | 0 | 0 | 4854 | 4947 |
| rr-explain-single | solvable | 24 | 21 | 87 | 23572 | 18 | 18 | 3 | 14694 | 8878 |
| rr-explain-single | impossible | 8 | 0 | 0 | 9759 | 2 | 0 | 0 | 4854 | 4905 |
| rr-plain | solvable | 24 | 22 | 90 | 24671 | 16 | 16 | 6 | 14421 | 10250 |
| rr-plain | impossible | 8 | 0 | 0 | 11581 | 1 | 0 | 0 | 4796 | 6785 |

## By category

### coding

| config | solved | score | cost | wave1 closed | wave2 closed |
| --- | ---: | ---: | ---: | ---: | ---: |
| nn-explain | 4/8 | 25 | 6455 | 4 | 0 |
| nn-explain-single | 5/8 | 28 | 4035 | 5 | 0 |
| nn-plain | 3/8 | 22 | 2937 | 3 | 0 |
| nn-single | 6/8 | 30 | 3952 | 5 | 1 |
| nr-explain | 3/8 | 17 | 5235 | 2 | 1 |
| nr-explain-single | 5/8 | 27 | 6672 | 5 | 0 |
| nr-plain | 5/8 | 27 | 3581 | 4 | 1 |
| route-search-r | 4/8 | 24 | 4864 | 3 | 1 |
| rr-explain | 6/8 | 30 | 8190 | 4 | 2 |
| rr-explain-single | 5/8 | 27 | 7214 | 5 | 0 |
| rr-plain | 5/8 | 27 | 7646 | 4 | 1 |

### data_analysis

| config | solved | score | cost | wave1 closed | wave2 closed |
| --- | ---: | ---: | ---: | ---: | ---: |
| nn-explain | 6/8 | 20 | 2394 | 6 | 0 |
| nn-explain-single | 6/8 | 20 | 2340 | 6 | 0 |
| nn-plain | 6/8 | 20 | 2577 | 5 | 1 |
| nn-single | 6/8 | 20 | 2477 | 6 | 0 |
| nr-explain | 6/8 | 20 | 2492 | 6 | 0 |
| nr-explain-single | 6/8 | 20 | 3150 | 6 | 0 |
| nr-plain | 6/8 | 20 | 2301 | 6 | 0 |
| route-search-r | 5/8 | 17 | 7238 | 4 | 1 |
| rr-explain | 5/8 | 19 | 9856 | 3 | 2 |
| rr-explain-single | 6/8 | 20 | 7233 | 5 | 1 |
| rr-plain | 6/8 | 20 | 6902 | 5 | 1 |

### math

| config | solved | score | cost | wave1 closed | wave2 closed |
| --- | ---: | ---: | ---: | ---: | ---: |
| nn-explain | 6/8 | 29 | 5083 | 5 | 1 |
| nn-explain-single | 6/8 | 29 | 5740 | 5 | 1 |
| nn-plain | 5/8 | 28 | 4879 | 4 | 1 |
| nn-single | 6/8 | 29 | 4771 | 5 | 1 |
| nr-explain | 6/8 | 29 | 6471 | 5 | 1 |
| nr-explain-single | 4/8 | 22 | 5609 | 3 | 1 |
| nr-plain | 6/8 | 29 | 4664 | 5 | 1 |
| route-search-r | 6/8 | 29 | 5482 | 5 | 1 |
| rr-explain | 6/8 | 29 | 6655 | 6 | 0 |
| rr-explain-single | 6/8 | 29 | 6562 | 6 | 0 |
| rr-plain | 6/8 | 29 | 8143 | 4 | 2 |

### search

| config | solved | score | cost | wave1 closed | wave2 closed |
| --- | ---: | ---: | ---: | ---: | ---: |
| nn-explain | 2/8 | 7 | 4299 | 1 | 1 |
| nn-explain-single | 4/8 | 12 | 5378 | 4 | 0 |
| nn-plain | 3/8 | 8 | 2501 | 3 | 0 |
| nn-single | 4/8 | 12 | 3344 | 2 | 2 |
| nr-explain | 3/8 | 9 | 4783 | 2 | 1 |
| nr-explain-single | 4/8 | 12 | 5940 | 3 | 1 |
| nr-plain | 3/8 | 9 | 8960 | 3 | 0 |
| route-search-r | 4/8 | 10 | 6524 | 4 | 0 |
| rr-explain | 3/8 | 10 | 15784 | 1 | 2 |
| rr-explain-single | 4/8 | 11 | 12322 | 2 | 2 |
| rr-plain | 5/8 | 14 | 13561 | 3 | 2 |

