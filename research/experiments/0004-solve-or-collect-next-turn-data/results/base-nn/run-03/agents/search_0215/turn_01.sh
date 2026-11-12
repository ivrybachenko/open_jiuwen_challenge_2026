cat << 'EOF' > solve.sh
#!/bin/bash

# Read the people.md file to find Lena Ortiz's mentor and employer
PEOPLE_FILE="kb/people.md"
COMPANIES_FILE="kb/companies.md"

# Extract Lena Ortiz's information
# We need to find the line with Lena Ortiz and get her mentor and employer
LENA_INFO=$(grep -A 10 "Lena Ortiz" "$PEOPLE_FILE" | head -20)

# Parse the mentor and employer from the file
# The format seems to be structured, let's look at the file first
echo "=== People File ==="
cat "$PEOPLE_FILE"
echo "=== Companies File ==="
cat "$COMPANIES_FILE"

# Let's parse more carefully
# Find Lena Ortiz's section and extract mentor and employer
MENTOR=$(grep -A 20 "Lena Ortiz" "$PEOPLE_FILE" | grep -i "mentor" | head -1 | sed 's/.*mentor[[:space:]]*[:=]*[[:space:]]*//' | sed 's/[[:space:]]*$//')
EMPLOYER=$(grep -A 20 "Lena Ortiz" "$PEOPLE_FILE" | grep -i "employer" | head -1 | sed 's/.*employer[[:space:]]*[:=]*[[:space:]]*//' | sed 's/[[:space:]]*$//')

echo "Lena Ortiz's mentor: '$MENTOR'"
echo "Lena Ortiz's employer: '$EMPLOYER'"

# Now find the mentor's employer
MENTOR_EMPLOYER=$(grep -A 20 "$MENTOR" "$PEOPLE_FILE" | grep -i "employer" | head -1 | sed 's/.*employer[[:space:]]*[:=]*[[:space:]]*//' | sed 's/[[:space:]]*$//')

echo "Mentor's employer: '$MENTOR_EMPLOYER'"

# Now find the headquarters city of the mentor's employer
CITY=$(grep -A 5 "$MENTOR_EMPLOYER" "$COMPANIES_FILE" | grep -i "headquarters" | head -1 | sed 's/.*headquarters[[:space:]]*[:=]*[[:space:]]*//' | sed 's/[[:space:]]*$//')

echo "City: '$CITY'"

# Write the answer
echo "$CITY" > answer.txt
echo "Answer written to answer.txt"
EOF

bash solve.sh