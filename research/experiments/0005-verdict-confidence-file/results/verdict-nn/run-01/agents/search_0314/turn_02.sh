# Find the user who made request req-8842 in logs/app.log and write to answer.txt
grep "req-8842" logs/app.log | head -1 | sed 's/.*user=\([^ ]*\).*/\1/' > answer.txt
cat answer.txt