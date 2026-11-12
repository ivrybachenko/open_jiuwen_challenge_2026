cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/base-nn/run-02/work/tasks/015_data_analysis_0316/workspace

python3 << 'EOF'
import csv

# Read the categories.csv file
categories = {}
with open('categories.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        category = row['category'].strip()
        parent = row['parent'].strip() if row['parent'] else None
        categories[category] = parent

# Find the top-level ancestor of 'alpha'
def find_top_ancestor(category, categories):
    visited = set()
    while category in categories and categories[category] is not None:
        if category in visited:
            return None  # Cycle detected
        visited.add(category)
        category = categories[category]
    return category

# Check if 'alpha' exists in the categories
if 'alpha' in categories:
    top_ancestor = find_top_ancestor('alpha', categories)
    print(f"Top-level ancestor of 'alpha': {top_ancestor}")
    with open('answer.txt', 'w') as f:
        f.write(top_ancestor if top_ancestor else '')
else:
    print("'alpha' not found in categories")
    with open('answer.txt', 'w') as f:
        f.write('NOT_FOUND')
EOF