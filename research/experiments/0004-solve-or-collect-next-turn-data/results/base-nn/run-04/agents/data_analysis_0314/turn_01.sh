cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/base-nn/run-04/work/tasks/014_data_analysis_0314/workspace && python3 -c "
import csv
total_sum = 0.0
with open('export.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            total_sum += float(row['total'])
        except (ValueError, KeyError):
            pass
# Round to avoid floating point issues, but keep as is if it's a clean number
# Let's print it first to see
print(f'Total: {total_sum}')
# Write the answer
with open('answer.txt', 'w') as f:
    f.write(str(total_sum))
"