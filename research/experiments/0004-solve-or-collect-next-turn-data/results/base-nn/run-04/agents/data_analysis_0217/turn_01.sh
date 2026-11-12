python3 -c "
import csv

with open('names.csv', 'r') as f:
    reader = csv.DictReader(f)
    names = [row['name'] for row in reader]

# Normalize: collapse runs of spaces, ignore case
normalized = set()
for name in names:
    # Collapse runs of spaces
    import re
    cleaned = re.sub(r'\s+', ' ', name).strip().lower()
    normalized.add(cleaned)

print(len(normalized))
with open('answer.txt', 'w') as f:
    f.write(str(len(normalized)) + '\n')
"