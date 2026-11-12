cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-nn/run-01/work/tasks/011_data_analysis_0217/workspace

python3 << 'EOF'
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

print(f"Distinct normalized names: {len(names)}")

with open('answer.txt', 'w') as f:
    f.write(str(len(names)) + '\n')
EOF