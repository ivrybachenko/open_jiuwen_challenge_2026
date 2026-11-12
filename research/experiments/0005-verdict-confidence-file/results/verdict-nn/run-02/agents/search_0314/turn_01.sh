grep "req-8842" logs/app.log | head -1 | awk '{print $1}' > answer.txt
cat answer.txt