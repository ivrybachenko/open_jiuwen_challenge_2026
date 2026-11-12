cat << 'EOF' > solve.sh
#!/bin/bash

# Read the people.md file to find Lena Ortiz's employer and mentor
PEOPLE_FILE="kb/people.md"

# Find Lena Ortiz's line and extract her employer and mentor
# We need to parse the markdown structure
# Let's first look at the structure

# Get the section for Lena Ortiz
# Assuming format like:
# ## Lena Ortiz
# - Employer: ...
# - Mentor: ...

# Use grep and awk/sed to extract info
# First, find the line with Lena Ortiz
LENALINE=$(grep -n "Lena Ortiz" "$PEOPLE_FILE" | head -1 | cut -d: -f1)

if [ -z "$LENALINE" ]; then
    echo "Could not find Lena Ortiz"
    echo "IMPOSSIBLE" > answer.txt
    exit 1
fi

# Get the next few lines after Lena Ortiz's line to find Employer and Mentor
# Read lines after Lena Ortiz's line
INFO=$(sed -n "$((LENALINE+1)),$((LENALINE+10))p" "$PEOPLE_FILE")

# Extract employer
EMPLOYER=$(echo "$INFO" | grep -i "Employer" | head -1 | sed 's/.*Employer[[:space:]]*:[[:space:]]*//' | sed 's/[[:space:]]*$//')

# Extract mentor
MENTOR=$(echo "$INFO" | grep -i "Mentor" | head -1 | sed 's/.*Mentor[[:space:]]*:[[:space:]]*//' | sed 's/[[:space:]]*$//')

echo "Lena Ortiz's Employer: $EMPLOYER"
echo "Lena Ortiz's Mentor: $MENTOR"

if [ -z "$EMPLOYER" ] || [ -z "$MENTOR" ]; then
    echo "Could not extract employer or mentor"
    echo "IMPOSSIBLE" > answer.txt
    exit 1
fi

# Now find the mentor's employer from the people.md file
# Find the mentor's section
MENTORLINE=$(grep -n "$MENTOR" "$PEOPLE_FILE" | head -1 | cut -d: -f1)

if [ -z "$MENTORLINE" ]; then
    echo "Could not find mentor $MENTOR"
    echo "IMPOSSIBLE" > answer.txt
    exit 1
fi

# Get the next few lines after mentor's line to find their employer
MENTORINFO=$(sed -n "$((MENTORLINE+1)),$((MENTORLINE+10))p" "$PEOPLE_FILE")

MENTOR_EMPLOYER=$(echo "$MENTORINFO" | grep -i "Employer" | head -1 | sed 's/.*Employer[[:space:]]*:[[:space:]]*//' | sed 's/[[:space:]]*$//')

echo "Mentor's Employer: $MENTOR_EMPLOYER"

if [ -z "$MENTOR_EMPLOYER" ]; then
    echo "Could not extract mentor's employer"
    echo "IMPOSSIBLE" > answer.txt
    exit 1
fi

# Now find the headquarters city of the mentor's employer from companies.md
COMPANIES_FILE="kb/companies.md"

# Search for the employer in companies.md
CITY=$(grep -i "$MENTOR_EMPLOYER" "$COMPANIES_FILE" | grep -i "headquarters" | sed 's/.*headquarters[[:space:]]*:[[:space:]]*//' | sed 's/[[:space:]]*$//')

if [ -z "$CITY" ]; then
    # Try case-insensitive search more broadly
    # Find the line with the company name
    COMPANYLINE=$(grep -i "$MENTOR_EMPLOYER" "$COMPANIES_FILE" | head -1)
    echo "Company line: $COMPANYLINE"
    CITY=$(echo "$COMPANYLINE" | sed 's/.*headquarters[[:space:]]*:[[:space:]]*//' | sed 's/[[:space:]]*$//')
fi

echo "City: $CITY"

if [ -z "$CITY" ]; then
    echo "Could not find headquarters city"
    echo "IMPOSSIBLE" > answer.txt
    exit 1
fi

# Write the answer
echo "$CITY" > answer.txt
echo "Answer written to answer.txt: $CITY"
EOF

bash solve.sh