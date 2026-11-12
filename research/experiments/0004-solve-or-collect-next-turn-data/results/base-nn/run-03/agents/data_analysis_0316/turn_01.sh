cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/base-nn/run-03/work/tasks/015_data_analysis_0316/workspace

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
    parent = row['parent']
    category_to_parent[category] = parent

# Find the top-level ancestor of 'alpha'
current = 'alpha'
visited = set()
while current in category_to_parent and category_to_parent[current] != '':
    if current in visited:
        break  # Avoid infinite loops
    visited.add(current)
    current = category_to_parent[current]

# The top-level ancestor is the one whose parent is empty
# If 'alpha' itself is top-level, its parent is empty
if current in category_to_parent and category_to_parent[current] == '':
    top_level_ancestor = current
else:
    # If we reached a node with no parent in the map, it's top-level
    top_level_ancestor = current

print(f"Top-level ancestor of 'alpha': {top_level_ancestor}")

# Write the answer to answer.txt
with open('answer.txt', 'w') as f:
    f.write(top_level_ancestor)
EOF