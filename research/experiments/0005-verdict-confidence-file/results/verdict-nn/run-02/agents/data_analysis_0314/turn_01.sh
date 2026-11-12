python3 -c "
import csv
total_sum = 0.0
with open('export.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        total_sum += float(row['total'])
# Round to avoid floating point issues, but keep as is if it's clean
# Let's print it to see
print(f'Total: {total_sum}')
# Write to answer.txt
with open('answer.txt', 'w') as f:
    f.write(f'{total_sum}')
"