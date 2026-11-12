cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-02/work/tasks/009_data_analysis_0208/workspace && python3 -c "
import csv
from collections import defaultdict

revenue_by_product = defaultdict(float)

with open('sales.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        units = float(row['units'])
        price = float(row['price'])
        product = row['product']
        revenue_by_product[product] += units * price

# Find the product with the largest total revenue
max_product = None
max_revenue = -1
for product, revenue in revenue_by_product.items():
    if revenue > max_revenue:
        max_revenue = revenue
        max_product = product

print(f'Max revenue product: {max_product} with revenue {max_revenue}')

with open('answer.txt', 'w') as f:
    f.write(max_product)
"