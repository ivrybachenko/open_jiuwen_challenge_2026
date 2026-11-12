cat << 'SCRIPT' > solve.sh
#!/bin/bash

# The file format is:
# - Name: mentor=X, employer=Y
# We need to parse this carefully.

# Step 1: Find Lena Ortiz's mentor
# From kb/people.md:
# - Lena Ortiz: mentor=Tom Reed, employer=Blue Harbor
# - Tom Reed: employer=Northwind Labs

# Extract Lena's mentor
LENA_MENTOR=$(grep "Lena Ortiz" kb/people.md | sed 's/.*mentor=\([^,]*\).*/\1/' | sed 's/[[:space:]]*$//')
echo "Lena's mentor: '$LENA_MENTOR'"

# Step 2: Find the mentor's employer
# We need to find the line for Tom Reed and extract his employer
MENTOR_EMPLOYER=$(grep "$LENA_MENTOR" kb/people.md | sed 's/.*employer=\([^,[:space:]]*\).*/\1/' | sed 's/[[:space:]]*$//')
echo "Mentor's employer: '$MENTOR_EMPLOYER'"

# Step 3: Find the city of the mentor's employer from companies.md
# From kb/companies.md:
# - Blue Harbor: city=Riga
# - Northwind Labs: city=Lisbon
CITY=$(grep "$MENTOR_EMPLOYER" kb/companies.md | sed 's/.*city=\([^[:space:]]*\).*/\1/' | sed 's/[[:space:]]*$//')
echo "City: '$CITY'"

# Write the answer
echo -n "$CITY" > answer.txt
echo "Answer written to answer.txt: $CITY"
SCRIPT

bash solve.sh