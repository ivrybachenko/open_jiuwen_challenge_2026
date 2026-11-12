cat << 'SCRIPT' > solve.sh
#!/bin/bash

# Read the people file
PEOPLE_FILE="kb/people.md"
COMPANIES_FILE="kb/companies.md"

# Step 1: Find Lena Ortiz's mentor
# The line is: - Lena Ortiz: mentor=Tom Reed, employer=Blue Harbor
# We need to extract the mentor name.
LENA_LINE=$(grep -i "Lena Ortiz" "$PEOPLE_FILE")
echo "Lena line: $LENA_LINE"

# Extract mentor name: after "mentor=" and before ","
LENA_MENTOR=$(echo "$LENA_LINE" | sed 's/.*mentor=//; s/,.*//')
echo "Lena's mentor: '$LENA_MENTOR'"

# Step 2: Find the mentor's employer
# The line for Tom Reed is: - Tom Reed: employer=Northwind Labs
MENTOR_LINE=$(grep -i "$LENA_MENTOR" "$PEOPLE_FILE")
echo "Mentor line: '$MENTOR_LINE'"

# Extract employer name: after "employer=" and before end of line (or comma if present)
MENTOR_EMPLOYER=$(echo "$MENTOR_LINE" | sed 's/.*employer=//; s/,.*//; s/[[:space:]]*$//')
echo "Mentor's employer: '$MENTOR_EMPLOYER'"

# Step 3: Find the city where the mentor's employer is headquartered
# The line for Northwind Labs is: - Northwind Labs: city=Lisbon
COMPANY_LINE=$(grep -i "$MENTOR_EMPLOYER" "$COMPANIES_FILE")
echo "Company line: '$COMPANY_LINE'"

# Extract city: after "city=" and before end of line
CITY=$(echo "$COMPANY_LINE" | sed 's/.*city=//; s/[[:space:]]*$//')
echo "City: '$CITY'"

# Write the answer
echo "$CITY" > answer.txt
echo "Answer written to answer.txt"
cat answer.txt
SCRIPT

bash solve.sh