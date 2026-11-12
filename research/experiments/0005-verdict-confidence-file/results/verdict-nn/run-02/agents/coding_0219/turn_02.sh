cat > top_products.py << 'EOF'
import csv
import sys
from collections import defaultdict

def main():
    args = sys.argv[1:]
    filename = None
    top_n = 3
    
    i = 0
    while i < len(args):
        if args[i] == '--top':
            if i + 1 < len(args):
                top_n = int(args[i + 1])
                i += 2
            else:
                print("Error: --top requires a value", file=sys.stderr)
                sys.exit(1)
        else:
            if filename is None:
                filename = args[i]
            i += 1
    
    if filename is None:
        print("Error: FILE argument required", file=sys.stderr)
        sys.exit(1)
    
    # Read CSV and sum units per product
    totals = defaultdict(int)
    with open(filename, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            product = row['product']
            units = int(row['units'])
            totals[product] += units
    
    # Sort by total (descending), then by product name (ascending) for ties
    sorted_products = sorted(totals.items(), key=lambda x: (-x[1], x[0]))
    
    # Print top N
    for product, total in sorted_products[:top_n]:
        print(f"{product} {total}")

if __name__ == '__main__':
    main()
EOF

python3 test_top_products.py

echo "DONE" > answer.txt