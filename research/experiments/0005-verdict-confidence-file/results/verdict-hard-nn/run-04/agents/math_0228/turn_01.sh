python3 -c "
from datetime import datetime, timedelta, timezone

# Departure: 2025-03-10 22:40 in UTC+8
dep_local = datetime(2025, 3, 10, 22, 40)
utc_plus_8 = timezone(timedelta(hours=8))
dep_utc = dep_local.replace(tzinfo=utc_plus_8) - timedelta(hours=8)

# Duration: 7 hours 25 minutes
duration = timedelta(hours=7, minutes=25)

# Arrival in UTC
arr_utc = dep_utc + duration

# Convert to UTC-5 local time
utc_minus_5 = timezone(timedelta(hours=-5))
arr_local = arr_utc.astimezone(utc_minus_5)

print(arr_local.strftime('%Y-%m-%d %H:%M'))
" > answer.txt