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

# Step 2: Parse the files to find the answer
# Find Lena Ortiz's employer
LENA_EMPLOYER=$(grep -i "Lena Ortiz" kb/people.md | sed 's/.*employer[[:space:]]*[:]*[[:space:]]*//' | sed 's/[[:space:]]*$//')
echo "Lena Ortiz's employer: '$LENA_EMPLOYER'"

# Find Lena Ortiz's mentor
LENA_MENTOR=$(grep -i "Lena Ortiz" kb/people.md | sed 's/.*mentor[[:space:]]*[:]*[[:space:]]*//' | sed 's/[[:space:]]*$//')
echo "Lena Ortiz's mentor: '$LENA_MENTOR'"

# Find the employer of Lena Ortiz's mentor
MENTOR_EMPLOYER=$(grep -i "$LENA_MENTOR" kb/people.md | sed 's/.*employer[[:space:]]*[:]*[[:space:]]*//' | sed 's/[[:space:]]*$//')
echo "Mentor's employer: '$MENTOR_EMPLOYER'"

# Find the headquarters city of the mentor's employer
CITY=$(grep -i "$MENTOR_EMPLOYER" kb/companies.md | sed 's/.*headquarters[[:space:]]*[:]*[[:space:]]*//' | sed 's/[[:space:]]*$//')
echo "City: '$CITY'"

# Write the answer
echo "$CITY" > answer.txt
echo "Answer written to answer.txt"
EOF

bash solve.sh