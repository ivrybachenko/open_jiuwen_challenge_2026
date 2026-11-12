cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/base-nn/run-02/work/tasks/009_data_analysis_0208/workspace && python3 -c "
import csv
from collections import defaultdict

revenue_by_product = defaultdict(float)

with open('sales.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        product = row['product']
        units = float(row['units'])
        price = float(row['price'])
        revenue_by_product[product] += units * price

# Find the product with the largest total revenue
max_product = max(revenue_by_product, key=revenue_by_product.get)

with open('answer.txt', 'w') as f:
    f.write(max_product)
"