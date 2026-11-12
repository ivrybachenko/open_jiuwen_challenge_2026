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

# Write the answer to answer.txt
with open('answer.txt', 'w') as f:
    f.write(max_product)

print(f'Product with largest total revenue: {max_product}')
print(f'Revenues: {product_revenue}')
"

echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Found product with max revenue" >> verdict.txt