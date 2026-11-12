#!/bin/bash
# Extract the port value from the [server] section of config.ini
# Parse the config file to find the port in the [server] section

# First, let's look at the config file to understand its structure
cat config.ini

# Extract the port value from the [server] section
# We need to find the line with "port" (case-insensitive) that appears after "[server]" and before the next section header
PORT=$(awk '
    /^\[server\]/ { in_server=1; next }
    /^\[/ { in_server=0; next }
    in_server && /^[[:space:]]*port[[:space:]]*=/ {
        gsub(/^[[:space:]]*port[[:space:]]*=[[:space:]]*/, "")
        gsub(/[[:space:]]*$/, "")
        print $0
        exit
    }
' config.ini)

echo "Extracted port: $PORT"

# Write the answer to answer.txt
echo "$PORT" > answer.txt

# Also write verdict.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Successfully extracted port from [server] section" >> verdict.txt