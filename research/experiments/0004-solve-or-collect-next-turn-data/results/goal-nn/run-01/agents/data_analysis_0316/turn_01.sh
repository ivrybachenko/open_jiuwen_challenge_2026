cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-01/work/tasks/015_data_analysis_0316/workspace

python3 << 'EOF'
import csv

# Read the categories.csv file
with open('categories.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Build a mapping from category to parent
parent_map = {}
for row in rows:
    category = row['category']
    parent = row['parent']
    parent_map[category] = parent

# Find the top-level ancestor of 'alpha'
current = 'alpha'
visited = set()
while current in parent_map and parent_map[current] != '':
    if current in visited:
        print(f"Cycle detected at {current}")
        break
    visited.add(current)
    current = parent_map[current]

# The top-level ancestor is the one whose parent is empty
# If 'alpha' itself is top-level, its parent is empty
if current not in parent_map or parent_map.get(current, '') == '':
    print(f"Top-level ancestor of alpha is: {current}")
    with open('answer.txt', 'w') as f:
        f.write(current)
else:
    print(f"Could not find top-level ancestor. Last seen: {current}")
EOF