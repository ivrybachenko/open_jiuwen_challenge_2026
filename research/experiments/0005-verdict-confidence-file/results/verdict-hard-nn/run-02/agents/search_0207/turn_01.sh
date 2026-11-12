# Extract the port value from the [server] section of config.ini
# Parse the config file to find the port in the [server] section

# First, let's look at the config file to understand its structure
cat config.ini

# Now extract the port value from the [server] section
# We need to find the line with "port" under the [server] section
PORT=$(awk '
    /^\[server\]/ { in_server=1; next }
    /^\[/ { in_server=0 }
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

# Create verdict.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Extracted port from [server] section of config.ini" >> verdict.txt