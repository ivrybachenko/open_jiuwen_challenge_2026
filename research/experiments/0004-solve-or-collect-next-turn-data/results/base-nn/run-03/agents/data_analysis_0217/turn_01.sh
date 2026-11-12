python3 -c "
import csv

names = set()
with open('names.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['name']
        # Collapse runs of spaces and ignore case
        normalized = ' '.join(name.lower().split())
        names.add(normalized)

print(len(names))
with open('answer.txt', 'w') as f:
    f.write(str(len(names)) + '\n')
"