cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-04/work/tasks/011_data_analysis_0217/workspace

python3 -c "
import csv
import re

names = set()
with open('names.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['name']
        # Collapse runs of spaces and ignore case
        normalized = re.sub(r'\s+', ' ', name).strip().lower()
        names.add(normalized)

print(len(names))
with open('answer.txt', 'w') as f:
    f.write(str(len(names)) + '\n')
"