cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/base-nn/run-04/work/tasks/015_data_analysis_0316/workspace

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
        break  # Avoid infinite loops
    visited.add(current)
    current = category_to_parent[current]

# The top-level ancestor is the one whose parent is empty
# If 'alpha' itself is top-level, it would be 'alpha'
if current not in category_to_parent or category_to_parent[current] == '':
    top_level_ancestor = current
else:
    # This shouldn't happen if the tree is well-formed
    top_level_ancestor = 'UNKNOWN'

print(f"Top-level ancestor of 'alpha': {top_level_ancestor}")

# Write the answer
with open('answer.txt', 'w') as f:
    f.write(top_level_ancestor)
EOF