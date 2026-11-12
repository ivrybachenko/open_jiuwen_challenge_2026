python3 << 'EOF'
import csv
import re
from datetime import datetime

# Read the CSV file
with open('events.csv', 'r') as f:
    reader = csv.DictReader(f)
    dates = []
    for row in reader:
        date_str = row['date'].strip()
        # Try different date formats
        try:
            # Try YYYY-MM-DD
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            dates.append(dt)
        except ValueError:
            try:
                # Try DD.MM.YYYY
                dt = datetime.strptime(date_str, '%d.%m.%Y')
                dates.append(dt)
            except ValueError:
                try:
                    # Try 'Month D, YYYY' (e.g., 'March 7, 2024')
                    dt = datetime.strptime(date_str, '%B %d, %Y')
                    dates.append(dt)
                except ValueError:
                    try:
                        # Try 'Month D, YYYY' with single digit day (e.g., 'March 7, 2024')
                        dt = datetime.strptime(date_str, '%B %d, %Y')
                        dates.append(dt)
                    except ValueError:
                        print(f"Could not parse date: {date_str}")
                        continue

if dates:
    earliest = min(dates)
    print(f"Earliest date: {earliest.strftime('%Y-%m-%d')}")
    with open('answer.txt', 'w') as f:
        f.write(earliest.strftime('%Y-%m-%d'))
else:
    print("No valid dates found")
    with open('answer.txt', 'w') as f:
        f.write("IMPOSSIBLE")
EOF