cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-nn/run-01/work/tasks/015_data_analysis_0316/workspace

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
while current in category_to_parent:
    parent = category_to_parent[current]
    if not parent:
        # This is a top-level category (no parent)
        break
    if parent in visited:
        # Cycle detected, break to avoid infinite loop
        break
    visited.add(current)
    current = parent

# The top-level ancestor is 'current' if it has no parent, or the last one we found
# If 'alpha' itself is top-level, current will be 'alpha'
# If 'alpha' has a parent, we traverse up until we find one with no parent

# Check if the final current is a top-level category (has no parent or parent is empty)
if current in category_to_parent:
    parent_of_current = category_to_parent[current]
    if parent_of_current:
        # This shouldn't happen if we traversed correctly, but just in case
        print(f"Warning: {current} still has a parent: {parent_of_current}")
        print(f"Visited: {visited}")
        print(f"Category to parent: {category_to_parent}")
    else:
        print(f"Top-level ancestor of alpha is: {current}")
        with open('answer.txt', 'w') as f:
            f.write(current)
else:
    # current is not in the mapping, meaning it's not a category in the file
    # This shouldn't happen if alpha is in the file
    print(f"Error: {current} is not in the categories file")
    with open('answer.txt', 'w') as f:
        f.write('NOT_FOUND')

# Debug: print all categories and parents
print("All categories and parents:")
for cat, par in category_to_parent.items():
    print(f"  {cat} -> {par}")
EOF