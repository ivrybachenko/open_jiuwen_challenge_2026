python3 -c "
from datetime import datetime, timedelta

# Departure: 2025-03-10 22:40 in UTC+8
departure_local = datetime(2025, 3, 10, 22, 40)
# Convert to UTC by subtracting 8 hours
departure_utc = departure_local - timedelta(hours=8)
# Add flight duration of 7 hours 25 minutes
arrival_utc = departure_utc + timedelta(hours=7, minutes=25)
# Convert arrival UTC to UTC-5 local time by subtracting 5 hours
arrival_local = arrival_utc - timedelta(hours=5)

print(arrival_local.strftime('%Y-%m-%d %H:%M'))
" > answer.txt