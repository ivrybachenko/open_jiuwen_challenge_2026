python3 << 'EOF'
import csv

# Read the CSV file
with open('names.csv', 'r', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    names = []
    for row in reader:
        name = row['name']
        # Normalize: collapse runs of spaces and ignore case
        normalized = ' '.join(name.split()).lower()
        names.append(normalized)

# Count distinct normalized names
distinct_names = set(names)
count = len(distinct_names)

# Write the answer
with open('answer.txt', 'w') as f:
    f.write(str(count))

print(f"Total names: {len(names)}")
print(f"Distinct normalized names: {count}")
EOF

echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Counted distinct normalized names from names.csv" >> verdict.txt