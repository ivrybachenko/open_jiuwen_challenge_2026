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
# A top-level category is one whose parent is empty.
# We need to find the ancestor of 'alpha' that is top-level.
# If there's a cycle, we need to handle it.

# First, let's identify all top-level categories
top_level_categories = set()
for cat, par in category_to_parent.items():
    if not par:
        top_level_categories.add(cat)

print(f"Top-level categories: {top_level_categories}")

# Now, find the top-level ancestor of 'alpha'
# We traverse up from 'alpha' until we reach a top-level category or detect a cycle.

current = 'alpha'
visited = set()
path = []

while current in category_to_parent:
    if current in visited:
        # Cycle detected
        print(f"Cycle detected at {current}")
        # In case of a cycle, there is no top-level ancestor
        with open('answer.txt', 'w') as f:
            f.write('CYCLE')
        break
    
    visited.add(current)
    path.append(current)
    parent = category_to_parent[current]
    
    if not parent:
        # Current is top-level
        print(f"Top-level ancestor of alpha is: {current}")
        with open('answer.txt', 'w') as f:
            f.write(current)
        break
    
    if parent in top_level_categories:
        # The parent is a top-level category
        print(f"Top-level ancestor of alpha is: {parent}")
        with open('answer.txt', 'w') as f:
            f.write(parent)
        break
    
    current = parent
else:
    # current is not in category_to_parent, meaning it's not a category in the file
    print(f"Error: {current} is not in the categories file")
    with open('answer.txt', 'w') as f:
        f.write('NOT_FOUND')

# Debug: print all categories and parents
print("All categories and parents:")
for cat, par in category_to_parent.items():
    print(f"  {cat} -> {par}")
EOF