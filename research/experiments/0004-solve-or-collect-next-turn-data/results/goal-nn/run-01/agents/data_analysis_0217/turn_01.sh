cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-01/work/tasks/011_data_analysis_0217/workspace

python3 -c "
import csv
import re

names = set()
with open('names.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['name']
        # Collapse runs of spaces
        name = re.sub(r'\s+', ' ', name)
        # Strip leading/trailing whitespace
        name = name.strip()
        # Ignore case
        name = name.lower()
        if name:  # skip empty
            names.add(name)

print(len(names))
with open('answer.txt', 'w') as f:
    f.write(str(len(names)) + '\n')
"