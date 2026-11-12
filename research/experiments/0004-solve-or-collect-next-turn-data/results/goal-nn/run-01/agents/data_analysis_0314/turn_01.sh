cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-01/work/tasks/014_data_analysis_0314/workspace

python3 -c "
import csv
total_sum = 0.0
with open('export.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            total_sum += float(row['total'])
        except (ValueError, KeyError):
            pass
# Round to avoid floating point issues, but keep as is if it's clean
print(total_sum)
" > answer.txt