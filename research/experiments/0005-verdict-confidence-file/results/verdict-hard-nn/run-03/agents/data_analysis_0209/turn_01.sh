python3 << 'EOF'
import csv

# Read customers to find those from Leeds
leeds_customers = set()
with open('customers.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['city'].strip() == 'Leeds':
            leeds_customers.add(row['customer_id'].strip())

# Read orders and calculate total revenue for Leeds customers
total_revenue = 0.0
with open('orders.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['customer_id'].strip() in leeds_customers:
            units = float(row['units'])
            price = float(row['price'])
            total_revenue += units * price

# Write the answer
with open('answer.txt', 'w') as f:
    f.write(str(int(total_revenue)) if total_revenue == int(total_revenue) else str(total_revenue))

print(f"Total revenue: {total_revenue}")
EOF

echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Calculated total revenue for Leeds customers" >> verdict.txt