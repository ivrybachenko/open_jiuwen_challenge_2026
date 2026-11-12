cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/base-nn/run-02/work/tasks/015_data_analysis_0316/workspace

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
    parent = category_to_parent[current]
    if parent == '':
        break
    current = parent

# If current is still 'alpha' and it has no parent, then alpha itself is top-level
# Otherwise, current is the top-level ancestor
if current == 'alpha' and category_to_parent.get('alpha', '') == '':
    print(f"alpha is a top-level category itself")
    answer = 'alpha'
else:
    answer = current

print(f"Top-level ancestor of alpha: {answer}")

# Write the answer to answer.txt
with open('answer.txt', 'w') as f:
    f.write(answer)
EOF