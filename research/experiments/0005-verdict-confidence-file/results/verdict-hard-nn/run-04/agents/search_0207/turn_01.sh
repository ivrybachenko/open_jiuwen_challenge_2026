# Extract the port value from the [server] section of config.ini
PORT=$(grep -A 10 '^\[server\]' config.ini | grep -i 'port' | head -1 | sed 's/.*=\s*//' | tr -d '[:space:]')

# Write the answer to answer.txt
echo "$PORT" > answer.txt

# Create verdict.txt as required
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Extracted port from [server] section" >> verdict.txt