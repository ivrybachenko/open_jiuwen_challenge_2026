cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-03/work/tasks/009_data_analysis_0208/workspace

python3 -c "
import csv

revenue_by_product = {}

with open('sales.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        product = row['product']
        units = int(row['units'])
        price = float(row['price'])
        revenue = units * price
        if product in revenue_by_product:
            revenue_by_product[product] += revenue
        else:
            revenue_by_product[product] = revenue

# Find the product with the largest total revenue
max_product = None
max_revenue = -1
for product, revenue in revenue_by_product.items():
    if revenue > max_revenue:
        max_revenue = revenue
        max_product = product

print(f'Total revenue by product: {revenue_by_product}')
print(f'Product with largest total revenue: {max_product}')

with open('answer.txt', 'w') as f:
    f.write(max_product)
"