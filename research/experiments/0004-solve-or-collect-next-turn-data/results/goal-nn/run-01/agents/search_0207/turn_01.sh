#!/bin/bash
# Extract the port value from the [server] section of config.ini
# and write it to answer.txt

# First, let's look at the config.ini file to understand its structure
cat config.ini

# Extract the port value from the [server] section
# We need to find the line with 'port' under the [server] section
PORT=$(awk '/^\[server\]/{found=1; next} /^\[/{found=0} found && /port/ {gsub(/[^0-9]/, "", $2); print $2; exit}' config.ini)

echo "Extracted port: $PORT"

# Write the answer to answer.txt
echo "$PORT" > answer.txt

# Verify the answer
cat answer.txt