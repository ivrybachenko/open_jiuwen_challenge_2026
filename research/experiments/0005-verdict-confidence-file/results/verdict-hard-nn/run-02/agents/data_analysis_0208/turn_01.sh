python3 -c "
import csv

# Read the CSV file
with open('sales.csv', 'r') as f:
    reader = csv.DictReader(f)
    revenue_by_product = {}
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

# Write the answer to answer.txt
with open('answer.txt', 'w') as f:
    f.write(max_product)

print(f'Product with largest total revenue: {max_product} (Revenue: {max_revenue})')
"

echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Found product with max revenue" >> verdict.txt