#!/bin/bash
# Extract the port value from the [server] section of config.ini
# The issue was that the awk script wasn't correctly parsing the port value

# Let's use a more robust approach with grep and sed
# First, extract the [server] section, then find the port line

PORT=$(sed -n '/^\[server\]/,/^\[/{/port/s/.*port[[:space:]]*=[[:space:]]*//p}' config.ini | head -1)

echo "Extracted port: '$PORT'"

# Write the answer to answer.txt
echo "$PORT" > answer.txt

# Verify the answer
cat answer.txt