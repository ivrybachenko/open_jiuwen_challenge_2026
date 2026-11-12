python3 -c "
import csv

seen = set()
with open('names.csv', 'r', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row['name']
        # Collapse runs of spaces and ignore case
        normalized = ' '.join(name.split()).lower()
        seen.add(normalized)

print(len(seen))
with open('answer.txt', 'w') as f:
    f.write(str(len(seen)) + '\n')
"