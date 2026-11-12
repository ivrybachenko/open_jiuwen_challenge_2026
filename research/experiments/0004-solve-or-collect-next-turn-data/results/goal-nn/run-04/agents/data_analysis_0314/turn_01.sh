cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-04/work/tasks/014_data_analysis_0314/workspace

python3 -c "
import csv
total_sum = 0.0
with open('export.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            total_sum += float(row['total'])
        except (ValueError, KeyError) as e:
            print(f'Error parsing row: {row}, error: {e}')
# Round to 2 decimal places for currency
print(round(total_sum, 2))
" > answer.txt