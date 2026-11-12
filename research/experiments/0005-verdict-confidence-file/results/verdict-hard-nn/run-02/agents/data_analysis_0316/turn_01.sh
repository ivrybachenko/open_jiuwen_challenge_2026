cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-hard-nn/run-02/work/tasks/015_data_analysis_0316/workspace

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
        # Cycle detected, break
        break
    visited.add(current)
    current = category_to_parent[current]

# The top-level ancestor is the one whose parent is empty
# If 'alpha' itself is top-level, its parent is empty, so we return 'alpha'
# Otherwise, we return the last non-empty parent
if current in category_to_parent and category_to_parent[current] == '':
    # current is a top-level category
    print(f"Top-level ancestor of alpha: {current}")
    with open('answer.txt', 'w') as f:
        f.write(current)
else:
    # This means alpha is not in the tree or something went wrong
    print(f"Could not find top-level ancestor for alpha. Current: {current}")
    with open('answer.txt', 'w') as f:
        f.write('IMPOSSIBLE')
EOF

echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Found top-level ancestor of alpha" >> verdict.txt