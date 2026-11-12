cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-04/work/tasks/009_data_analysis_0208/workspace

python3 -c "
import csv

# Read the CSV file
with open('sales.csv', 'r') as f:
    reader = csv.DictReader(f)
    product_revenue = {}
    for row in reader:
        product = row['product']
        units = int(row['units'])
        price = float(row['price'])
        revenue = units * price
        if product in product_revenue:
            product_revenue[product] += revenue
        else:
            product_revenue[product] = revenue

# Find the product with the largest total revenue
max_product = max(product_revenue, key=product_revenue.get)
print(f'Product with largest total revenue: {max_product}')
print(f'Total revenue: {product_revenue[max_product]}')

# Write the answer to answer.txt
with open('answer.txt', 'w') as f:
    f.write(max_product)
"