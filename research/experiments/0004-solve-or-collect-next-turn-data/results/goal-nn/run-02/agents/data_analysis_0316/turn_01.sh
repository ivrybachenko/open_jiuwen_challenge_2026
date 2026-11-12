cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-02/work/tasks/015_data_analysis_0316/workspace

python3 << 'EOF'
import csv

# Read the categories.csv file
with open('categories.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Build a mapping from category to parent
category_to_parent = {}
for row in rows:
    category = row['category']
    parent = row['parent'].strip() if row['parent'] else ''
    category_to_parent[category] = parent

# Find the top-level ancestor of 'alpha'
current = 'alpha'
visited = set()
while current in category_to_parent and category_to_parent[current] != '':
    if current in visited:
        print(f"Cycle detected at {current}")
        break
    visited.add(current)
    current = category_to_parent[current]

# current is now the top-level ancestor (or 'alpha' itself if it's top-level)
print(f"Top-level ancestor of 'alpha': {current}")

# Write the answer
with open('answer.txt', 'w') as f:
    f.write(current)
EOF