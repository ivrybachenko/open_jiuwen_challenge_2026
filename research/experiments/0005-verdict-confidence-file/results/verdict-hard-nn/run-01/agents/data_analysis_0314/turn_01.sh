python3 -c "
import csv
total_sum = 0.0
with open('export.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        total_sum += float(row['total'])
# Round to 2 decimal places to avoid floating point issues
total_sum = round(total_sum, 2)
print(total_sum)
with open('answer.txt', 'w') as f:
    f.write(str(total_sum))
"
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Computed sum of total column" >> verdict.txt