cat << 'SCRIPT' > solve.sh
#!/bin/bash

# Read the files
PEOPLE_FILE="kb/people.md"
COMPANIES_FILE="kb/companies.md"

echo "=== People File ==="
cat "$PEOPLE_FILE"
echo "=== Companies File ==="
cat "$COMPANIES_FILE"

# Parse people.md line by line
# Format: - Name: mentor=X, employer=Y
# We need:
# 1. Lena Ortiz's mentor -> Tom Reed
# 2. Tom Reed's employer -> Northwind Labs
# 3. Northwind Labs' city -> ?

# Step 1: Find Lena Ortiz's mentor
LENA_MENTOR=$(grep "Lena Ortiz" "$PEOPLE_FILE" | sed 's/.*mentor=\([^,]*\).*/\1/' | sed 's/[[:space:]]*$//')
echo "Lena Ortiz's mentor: '$LENA_MENTOR'"

# Step 2: Find the mentor's employer
MENTOR_EMPLOYER=$(grep "$LENA_MENTOR" "$PEOPLE_FILE" | sed 's/.*employer=\([^,]*\).*/\1/' | sed 's/[[:space:]]*$//')
echo "Mentor's employer: '$MENTOR_EMPLOYER'"

# Step 3: Find the city of that employer from companies.md
CITY=$(grep "$MENTOR_EMPLOYER" "$COMPANIES_FILE" | sed 's/.*city=\([^,]*\).*/\1/' | sed 's/[[:space:]]*$//')
echo "City: '$CITY'"

# Write answer
echo "$CITY" > answer.txt
echo "Answer written to answer.txt"
SCRIPT

bash solve.sh