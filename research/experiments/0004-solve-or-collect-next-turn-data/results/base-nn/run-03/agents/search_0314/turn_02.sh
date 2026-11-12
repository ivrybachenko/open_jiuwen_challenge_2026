grep "req-8842" logs/app.log > /tmp/req8842_line.txt
cat /tmp/req8842_line.txt
# Try to extract the user from the log line using sed or awk
# First, let's see the format of the log line
head -1 logs/app.log > /tmp/sample_line.txt
cat /tmp/sample_line.txt
# Extract user field - try common patterns like "user: X", "user=X", "user X"
sed -n 's/.*[Uu]ser[=: ]*\([^ ,]*\).*/\1/p' /tmp/req8842_line.txt > answer.txt
# If that didn't work, try another pattern
if [ ! -s answer.txt ]; then
    grep -o '[Uu]ser[=: ]*[A-Za-z0-9_-]*' /tmp/req8842_line.txt | sed 's/[Uu]ser[=: ]*//' > answer.txt
fi
# If still empty, try to find any word that looks like a username near req-8842
if [ ! -s answer.txt ]; then
    grep -oE '[A-Za-z][A-Za-z0-9_-]*' /tmp/req8842_line.txt | head -5 > answer.txt
fi
cat answer.txt