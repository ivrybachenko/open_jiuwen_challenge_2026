cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/base-nn/run-04/work/tasks/008_data_analysis_0206/workspace

python3 -c "
import csv

count = 0
with open('sales.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['region'] == 'West' and int(row['units']) > 10:
            count += 1

with open('answer.txt', 'w') as f:
    f.write(str(count))
"