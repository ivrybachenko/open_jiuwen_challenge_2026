cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-nn/run-01/work/tasks/012_data_analysis_0225/workspace

python3 << 'EOF'
import csv
import re
from datetime import datetime

dates = []

with open('events.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        date_str = row['date'].strip()
        # Try YYYY-MM-DD
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            dates.append(dt)
            continue
        except ValueError:
            pass
        # Try DD.MM.YYYY
        try:
            dt = datetime.strptime(date_str, '%d.%m.%Y')
            dates.append(dt)
            continue
        except ValueError:
            pass
        # Try Month D, YYYY (e.g., "March 5, 2024")
        try:
            dt = datetime.strptime(date_str, '%B %d, %Y')
            dates.append(dt)
            continue
        except ValueError:
            pass
        # Try Month D YYYY (without comma)
        try:
            dt = datetime.strptime(date_str, '%B %d %Y')
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