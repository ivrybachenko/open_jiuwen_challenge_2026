python3 -c "
from datetime import datetime, timedelta

# Departure: 2025-03-10 22:40 in UTC+8
# Convert to UTC: subtract 8 hours
departure_utc = datetime(2025, 3, 10, 22, 40) - timedelta(hours=8)
# departure_utc = 2025-03-10 14:40 UTC

# Add flight duration: 7 hours 25 minutes
arrival_utc = departure_utc + timedelta(hours=7, minutes=25)
# arrival_utc = 2025-03-10 22:05 UTC

# Convert to UTC-5: subtract 5 hours
arrival_local = arrival_utc - timedelta(hours=5)
# arrival_local = 2025-03-10 17:05

print(arrival_local.strftime('%Y-%m-%d %H:%M'))
" > answer.txt