cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/base-nn/run-01/work/tasks/015_data_analysis_0316/workspace

python3 << 'EOF'
import csv

# Read the categories.csv file
categories = {}
with open('categories.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        category = row['category'].strip()
        parent = row['parent'].strip() if row['parent'] else ''
        categories[category] = parent

print("Categories:", categories)

# Find the top-level ancestor of 'alpha'
current = 'alpha'
visited = set()
path = []
while current in categories:
    if current in visited:
        print(f"Cycle detected at {current}")
        break
    visited.add(current)
    path.append(current)
    parent = categories[current]
    if parent == '':
        # current is a top-level category
        print(f"Top-level ancestor of alpha is: {current}")
        with open('answer.txt', 'w') as f:
            f.write(current)
        break
    current = parent
else:
    if current not in categories:
        print(f"Category {current} not found in categories")
    else:
        print(f"Could not find top-level ancestor, last seen: {current}")
EOF