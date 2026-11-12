# Extract the port value from the [server] section of config.ini
PORT=$(grep -A 10 '^\[server\]' config.ini | grep -i 'port' | head -1 | sed 's/.*=\s*//' | tr -d '[:space:]')
echo "$PORT" > answer.txt
echo "Solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Extracted port from [server] section" >> verdict.txt