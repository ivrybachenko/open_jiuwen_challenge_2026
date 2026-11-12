#!/bin/bash

# Inspect all files
echo "=== top_products.py ==="
cat top_products.py
echo "=== test_top_products.py ==="
cat test_top_products.py
echo "=== orders.csv ==="
cat orders.csv

# Now fix top_products.py
cat > top_products.py << 'PYEOF'
import csv
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='Top products by units')
    parser.add_argument('file', help='CSV file with product,units columns')
    parser.add_argument('--top', type=int, default=3, help='Number of top products to show')
    args = parser.parse_args()

    # Read CSV and sum units per product
    totals = {}
    with open(args.file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            product = row['product']
            units = int(row['units'])
            totals[product] = totals.get(product, 0) + units

    # Sort by total descending, then by product name ascending for ties
    sorted_products = sorted(totals.items(), key=lambda x: (-x[1], x[0]))

    # Print top N
    for product, total in sorted_products[:args.top]:
        print(f"{product} {total}")

if __name__ == '__main__':
    main()
PYEOF

# Run the tests
python3 test_top_products.py

# Check if tests pass
if [ $? -eq 0 ]; then
    echo "DONE" > answer.txt
    echo "solved" > verdict.txt
    echo "1.00" >> verdict.txt
    echo "Tests pass, answer written" >> verdict.txt
else
    echo "not_solved" > verdict.txt
    echo "0.00" >> verdict.txt
    echo "Tests still failing" >> verdict.txt
fi