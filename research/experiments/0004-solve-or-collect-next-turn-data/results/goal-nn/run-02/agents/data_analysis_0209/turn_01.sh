cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-02/work/tasks/010_data_analysis_0209/workspace

python3 << 'EOF'
import csv

# Read customers to find those from Leeds
leeds_customer_ids = set()
with open('customers.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['city'].strip() == 'Leeds':
            leeds_customer_ids.add(row['customer_id'].strip())

# Read orders and calculate total revenue for Leeds customers
total_revenue = 0
with open('orders.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['customer_id'].strip() in leeds_customer_ids:
            units = int(row['units'].strip())
            price = float(row['price'].strip())
            total_revenue += units * price

# Write the answer
with open('answer.txt', 'w') as f:
    f.write(str(int(total_revenue)) if total_revenue == int(total_revenue) else str(total_revenue))

print(f"Total revenue: {total_revenue}")
EOF