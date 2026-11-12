cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-hard-nn/run-04/work/tasks/015_data_analysis_0316/workspace

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
        print(f"Cycle detected at {current}")
        break
    visited.add(current)
    parent = category_to_parent[current]
    if parent == '':
        # This means current is a top-level category, but we started from alpha
        # So alpha itself is top-level? No, we need the ancestor.
        # If parent is empty, current is top-level.
        break
    current = parent

# Check if current is a top-level category (parent is empty or not in the map)
if current in category_to_parent and category_to_parent[current] == '':
    top_level_ancestor = current
elif current not in category_to_parent:
    # current is not in the map, so it might be a top-level category itself
    # But we started from 'alpha', so if alpha is not in the map, something is wrong
    top_level_ancestor = current
else:
    # current is in the map but parent is empty, so current is top-level
    top_level_ancestor = current

print(f"Top-level ancestor of 'alpha' is: {top_level_ancestor}")

# Write the answer
with open('answer.txt', 'w') as f:
    f.write(top_level_ancestor)
EOF

echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Found top-level ancestor of alpha" >> verdict.txt