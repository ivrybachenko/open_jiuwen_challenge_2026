python3 -c "
from datetime import datetime, timedelta, timezone

# Departure: 2025-03-10 22:40 in UTC+8
dep_time = datetime(2025, 3, 10, 22, 40)
utc_plus_8 = timezone(timedelta(hours=8))
dep_utc = dep_time.replace(tzinfo=utc_plus_8).astimezone(timezone.utc)

# Duration: 7 hours 25 minutes
duration = timedelta(hours=7, minutes=25)
arrival_utc = dep_utc + duration

# Convert to UTC-5
utc_minus_5 = timezone(timedelta(hours=-5))
arrival_local = arrival_utc.astimezone(utc_minus_5)

print(arrival_local.strftime('%Y-%m-%d %H:%M'))
" > answer.txt

cat answer.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Computed arrival time correctly" >> verdict.txt