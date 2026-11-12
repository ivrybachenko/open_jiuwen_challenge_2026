cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-04/work/tasks/003_coding_0219/workspace && cat > top_products.py << 'EOF'
import csv
import sys
import argparse
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description="Top products by units")
    parser.add_argument("file", help="CSV file with product,units columns")
    parser.add_argument("--top", type=int, default=3, help="Number of top products to show")
    args = parser.parse_args()

    totals = defaultdict(int)
    with open(args.file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            totals[row['product']] += int(row['units'])

    # Sort by total descending, then by product name ascending for ties
    sorted_products = sorted(totals.items(), key=lambda x: (-x[1], x[0]))

    for product, total in sorted_products[:args.top]:
        print(f"{product} {total}")

if __name__ == "__main__":
    main()
EOF
python3 test_top_products.py && echo "DONE" > answer.txt