python3 -c "
import csv
count = 0
with open('sales.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['region'] == 'West' and int(row['units']) > 10:
            count += 1
with open('answer.txt', 'w') as f:
    f.write(str(count))
"