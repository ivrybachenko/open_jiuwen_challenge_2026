cat << 'EOF' > solve.sh
#!/bin/bash

# Step 1: Find Lena Ortiz's employer from kb/people.md
# We need to find the line with "Lena Ortiz" and extract her employer.
# Let's first look at the structure of the file.
echo "=== kb/people.md ==="
cat kb/people.md

echo ""
echo "=== kb/companies.md ==="
cat kb/companies.md

# Parse the people file to find Lena Ortiz's employer
# Assuming a format like: Name: ..., Employer: ..., Mentor: ...
# Let's use grep and sed/awk to extract the information.

# Find the section for Lena Ortiz
# Let's assume the file has entries separated by blank lines or some delimiter.
# Let's first see the raw content more carefully.

# Extract the block containing "Lena Ortiz"
LENABLOCK=$(grep -A 10 "Lena Ortiz" kb/people.md | head -n 10)
echo "Lena's block:"
echo "$LENABLOCK"

# Extract employer from Lena's block
LENA_EMPLOYER=$(echo "$LENABLOCK" | grep -i "employer" | sed 's/.*[Ee]mployer[[:space:]]*[:]*[[:space:]]*//' | sed 's/[[:space:]]*$//')
echo "Lena's employer: '$LENA_EMPLOYER'"

# Extract mentor from Lena's block
LENA_MENTOR=$(echo "$LENABLOCK" | grep -i "mentor" | sed 's/.*[Mm]entor[[:space:]]*[:]*[[:space:]]*//' | sed 's/[[:space:]]*$//')
echo "Lena's mentor: '$LENA_MENTOR'"

# Now find the mentor's employer
# Search for the mentor's name in the people file
MENTORBLOCK=$(grep -A 10 "$LENA_MENTOR" kb/people.md | head -n 10)
echo "Mentor's block:"
echo "$MENTORBLOCK"

MENTOR_EMPLOYER=$(echo "$MENTORBLOCK" | grep -i "employer" | sed 's/.*[Ee]mployer[[:space:]]*[:]*[[:space:]]*//' | sed 's/[[:space:]]*$//')
echo "Mentor's employer: '$MENTOR_EMPLOYER'"

# Now find the headquarters city of the mentor's employer from companies.md
echo ""
echo "Searching for '$MENTOR_EMPLOYER' in companies.md"
CITY=$(grep -i "$MENTOR_EMPLOYER" kb/companies.md | sed 's/.*[Cc]ity[[:space:]]*[:]*[[:space:]]*//' | sed 's/[[:space:]]*$//')
echo "City: '$CITY'"

# Write the answer
echo -n "$CITY" > answer.txt
echo "Answer written to answer.txt: $CITY"
EOF

bash solve.sh