python3 -c "
import csv

with open('names.csv', 'r') as f:
    reader = csv.DictReader(f)
    names = [row['name'] for row in reader]

# Normalize: collapse runs of spaces, ignore case
import re
normalized = set()
for name in names:
    # Collapse runs of whitespace to single space, strip, lowercase
    norm = re.sub(r'\s+', ' ', name.strip()).lower()
    normalized.add(norm)

print(f'Total names: {len(names)}')
print(f'Distinct normalized names: {len(normalized)}')

with open('answer.txt', 'w') as f:
    f.write(str(len(normalized)) + '\n')
"

echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Counted distinct normalized names from names.csv" >> verdict.txt