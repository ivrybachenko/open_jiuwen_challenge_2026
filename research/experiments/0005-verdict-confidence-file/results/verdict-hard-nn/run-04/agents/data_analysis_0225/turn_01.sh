cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-hard-nn/run-04/work/tasks/012_data_analysis_0225/workspace

python3 << 'EOF'
import csv
import re
from datetime import datetime

# Read the CSV file
with open('events.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    dates = []
    for row in reader:
        if len(row) >= 2:
            event_id, date_str = row[0], row[1]
            date_str = date_str.strip()
            
            # Try to parse the date in various formats
            parsed_date = None
            
            # Try YYYY-MM-DD
            try:
                parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                pass
            
            # Try DD.MM.YYYY
            if parsed_date is None:
                try:
                    parsed_date = datetime.strptime(date_str, '%d.%m.%Y')
                except ValueError:
                    pass
            
            # Try 'Month D, YYYY' (e.g., 'March 7, 2024')
            if parsed_date is None:
                try:
                    parsed_date = datetime.strptime(date_str, '%B %d, %Y')
                except ValueError:
                    pass
            
            # Try 'Month D YYYY' (without comma)
            if parsed_date is None:
                try:
                    parsed_date = datetime.strptime(date_str, '%B %d %Y')
                except ValueError:
                    pass
            
            if parsed_date:
                dates.append(parsed_date)

if dates:
    earliest = min(dates)
    answer = earliest.strftime('%Y-%m-%d')
    print(f"Earliest date: {answer}")
    with open('answer.txt', 'w') as f:
        f.write(answer)
else:
    print("No valid dates found")
    with open('answer.txt', 'w') as f:
        f.write("IMPOSSIBLE")

EOF

echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Found earliest date from events.csv" >> verdict.txt