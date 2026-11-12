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
        # YYYY-MM-DD
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            dates.append(dt)
            continue
        except ValueError:
            pass
        # DD.MM.YYYY
        try:
            dt = datetime.strptime(date_str, '%d.%m.%Y')
            dates.append(dt)
            continue
        except ValueError:
            pass
        # Month D, YYYY (e.g., "March 7, 2024")
        try:
            dt = datetime.strptime(date_str, '%B %d, %Y')
            dates.append(dt)
            continue
        except ValueError:
            pass
        # Try with single digit day (e.g., "March 7, 2024" vs "March 07, 2024")
        # The %d should handle both, but let's try %b for abbreviated month
        try:
            dt = datetime.strptime(date_str, '%b %d, %Y')
            dates.append(dt)
            continue
        except ValueError:
            pass

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