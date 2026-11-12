grep "req-8842" logs/app.log > /tmp/req8842_line.txt
cat /tmp/req8842_line.txt
# Try to extract user from the log line using sed or awk
# First, let's see the format of the log line
head -1 logs/app.log > /tmp/sample_line.txt
cat /tmp/sample_line.txt
# Extract user field - try common patterns like user=XXX or "user": "XXX"
sed -n 's/.*user[=: ]*\([^ ,}"]*\).*/\1/p' /tmp/req8842_line.txt > answer.txt
# If that didn't work, try another pattern
if [ ! -s answer.txt ]; then
    grep -o 'user[^ ,}"]*' /tmp/req8842_line.txt | head -1 | sed 's/user[=: ]*//' > answer.txt
fi
# If still empty, try JSON-like pattern
if [ ! -s answer.txt ]; then
    grep -o '"user"[[:space:]]*:[[:space:]]*"[^"]*"' /tmp/req8842_line.txt | head -1 | sed 's/.*"user"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' > answer.txt
fi
cat answer.txt