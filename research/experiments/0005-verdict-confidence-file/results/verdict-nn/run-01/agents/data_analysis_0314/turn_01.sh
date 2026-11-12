python3 -c "
import csv
total = 0.0
with open('export.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        total += float(row['total'])
# Round to avoid floating point issues, but keep as is if it's clean
print(f'{total:.2f}')
with open('answer.txt', 'w') as f:
    f.write(f'{total:.2f}\n')
"