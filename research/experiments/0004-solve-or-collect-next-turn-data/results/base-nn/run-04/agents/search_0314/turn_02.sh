grep "req-8842" logs/app.log > /tmp/req8842_line.txt
cat /tmp/req8842_line.txt
# Try to extract the user from the log line using sed or awk
# First, let's see the format of the log line
head -1 logs/app.log > /tmp/sample_line.txt
cat /tmp/sample_line.txt
# Extract user field - try common patterns like "user: X", "user=X", "username: X"
sed -n 's/.*user[=: ]*\([^ ,]*\).*/\1/p' /tmp/req8842_line.txt > answer.txt
# If that didn't work, try other patterns
if [ ! -s answer.txt ]; then
    sed -n 's/.*username[=: ]*\([^ ,]*\).*/\1/p' /tmp/req8842_line.txt > answer.txt
fi
if [ ! -s answer.txt ]; then
    sed -n 's/.*User[=: ]*\([^ ,]*\).*/\1/p' /tmp/req8842_line.txt > answer.txt
fi
if [ ! -s answer.txt ]; then
    sed -n 's/.*user_id[=: ]*\([^ ,]*\).*/\1/p' /tmp/req8842_line.txt > answer.txt
fi
cat answer.txt