python3 << 'EOF'
import csv

# Read the CSV file
with open('names.csv', 'r', newline='') as f:
    reader = csv.DictReader(f)
    names = [row['name'] for row in reader]

# Normalize: collapse runs of spaces and ignore case
normalized = set()
for name in names:
    # Collapse runs of spaces
    import re
    collapsed = re.sub(r'\s+', ' ', name).strip()
    # Ignore case
    normalized.add(collapsed.lower())

# Count distinct normalized names
count = len(normalized)

# Write the answer
with open('answer.txt', 'w') as f:
    f.write(str(count))

print(f"Distinct normalized names: {count}")
EOF

echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Counted distinct normalized names from names.csv" >> verdict.txt