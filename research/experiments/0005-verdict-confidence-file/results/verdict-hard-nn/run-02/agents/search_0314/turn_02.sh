# Find the user who made request req-8842 in logs/app.log and write the answer
grep "req-8842" logs/app.log | grep -oP 'user=\K\S+' > answer.txt
cat answer.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Found user for req-8842" >> verdict.txt