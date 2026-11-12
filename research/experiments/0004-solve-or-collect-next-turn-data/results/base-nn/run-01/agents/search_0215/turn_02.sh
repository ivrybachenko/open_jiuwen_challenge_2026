cat << 'SCRIPT' > solve.sh
#!/bin/bash

# First, let's inspect the files to understand their structure
echo "=== kb/people.md ==="
cat kb/people.md
echo ""
echo "=== kb/companies.md ==="
cat kb/companies.md
echo ""

# Now let's parse properly
# Read the entire people.md file
PEOPLE=$(cat kb/people.md)

# Find Lena Ortiz's section. We need to find the block for Lena Ortiz.
# Let's use a different approach: split by person entries and find Lena Ortiz.

# Use awk to extract Lena Ortiz's info
# Strategy: find the line with "Lena Ortiz", then read subsequent lines until next person or end
# Let's first see the structure more clearly

# Find the line number of Lena Ortiz
LENALINE=$(grep -n "Lena Ortiz" kb/people.md | head -1 | cut -d: -f1)
echo "Lena Ortiz found at line: $LENALINE"

# Get lines from Lena Ortiz's line to the next person's line (or end of file)
TOTAL_LINES=$(wc -l < kb/people.md)
NEXT_PERSON_LINE=$(tail -n +$((LENALINE+1)) kb/people.md | grep -n "^[A-Z]" | head -1 | cut -d: -f1)

if [ -z "$NEXT_PERSON_LINE" ]; then
    END_LINE=$TOTAL_LINES
else
    END_LINE=$((LENALINE + NEXT_PERSON_LINE - 1))
fi

echo "Lena Ortiz section: lines $LENALINE to $END_LINE"

LENASECTION=$(sed -n "${LENALINE},${END_LINE}p" kb/people.md)
echo "Lena Ortiz section content:"
echo "$LENASECTION"
echo ""

# Extract employer from Lena's section
# Look for patterns like "Employer: X" or "employer=X" or similar
LENA_EMPLOYER=$(echo "$LENASECTION" | grep -i "employer" | head -1 | sed 's/.*[Ee]mployer[[:space:]]*[:=][[:space:]]*//' | sed 's/[[:space:]]*$//')
echo "Lena's employer (raw): '$LENA_EMPLOYER'"

# Extract mentor from Lena's section
LENA_MENTOR=$(echo "$LENASECTION" | grep -i "mentor" | head -1 | sed 's/.*[Mm]entor[[:space:]]*[:=][[:space:]]*//' | sed 's/[[:space:]]*$//')
echo "Lena's mentor (raw): '$LENA_MENTOR'"

# Clean up the employer name - it might have extra text
# Let's also check if the employer line has a different format
if [ -z "$LENA_EMPLOYER" ]; then
    # Try alternative patterns
    LENA_EMPLOYER=$(echo "$LENASECTION" | grep -i "company" | head -1 | sed 's/.*[Cc]ompany[[:space:]]*[:=][[:space:]]*//' | sed 's/[[:space:]]*$//')
    echo "Lena's employer (from company): '$LENA_EMPLOYER'"
fi

if [ -z "$LENA_MENTOR" ]; then
    # Try alternative patterns
    LENA_MENTOR=$(echo "$LENASECTION" | grep -i "advisor" | head -1 | sed 's/.*[Aa]dvisor[[:space:]]*[:=][[:space:]]*//' | sed 's/[[:space:]]*$//')
    echo "Lena's mentor (from advisor): '$LENA_MENTOR'"
fi

echo "Final Lena's employer: '$LENA_EMPLOYER'"
echo "Final Lena's mentor: '$LENA_MENTOR'"

if [ -z "$LENA_EMPLOYER" ] || [ -z "$LENA_MENTOR" ]; then
    echo "IMPOSSIBLE: Could not extract employer or mentor for Lena Ortiz"
    echo "IMPOSSIBLE" > answer.txt
    exit 0
fi

# Now find the mentor's employer
# Search for the mentor in people.md
MENTORLINE=$(grep -n "$LENA_MENTOR" kb/people.md | head -1 | cut -d: -f1)
echo "Mentor $LENA_MENTOR found at line: $MENTORLINE"

if [ -z "$MENTORLINE" ]; then
    echo "IMPOSSIBLE: Could not find mentor $LENA_MENTOR in people.md"
    echo "IMPOSSIBLE" > answer.txt
    exit 0
fi

# Get mentor's section
MENTORNEXT=$(tail -n +$((MENTORLINE+1)) kb/people.md | grep -n "^[A-Z]" | head -1 | cut -d: -f1)
if [ -z "$MENTORNEXT" ]; then
    MENTOREND=$TOTAL_LINES
else
    MENTOREND=$((MENTORLINE + MENTORNEXT - 1))
fi

MENTORSECTION=$(sed -n "${MENTORLINE},${MENTOREND}p" kb/people.md)
echo "Mentor section content:"
echo "$MENTORSECTION"
echo ""

# Extract mentor's employer
MENTOR_EMPLOYER=$(echo "$MENTORSECTION" | grep -i "employer" | head -1 | sed 's/.*[Ee]mployer[[:space:]]*[:=][[:space:]]*//' | sed 's/[[:space:]]*$//')
echo "Mentor's employer (raw): '$MENTOR_EMPLOYER'"

if [ -z "$MENTOR_EMPLOYER" ]; then
    MENTOR_EMPLOYER=$(echo "$MENTORSECTION" | grep -i "company" | head -1 | sed 's/.*[Cc]ompany[[:space:]]*[:=][[:space:]]*//' | sed 's/[[:space:]]*$//')
    echo "Mentor's employer (from company): '$MENTOR_EMPLOYER'"
fi

echo "Final Mentor's employer: '$MENTOR_EMPLOYER'"

if [ -z "$MENTOR_EMPLOYER" ]; then
    echo "IMPOSSIBLE: Could not extract mentor's employer"
    echo "IMPOSSIBLE" > answer.txt
    exit 0
fi

# Now find the headquarters city of the mentor's employer from companies.md
COMPANIES=$(cat kb/companies.md)
echo ""
echo "=== Searching for company: $MENTOR_EMPLOYER ==="

# Search for the company in companies.md
# Try exact match first, then case-insensitive
CITY=$(grep -i "$MENTOR_EMPLOYER" kb/companies.md | grep -i "headquarters" | head -1 | sed 's/.*[Hh]eadquarters[[:space:]]*[:=][[:space:]]*//' | sed 's/[[:space:]]*$//')

echo "City (raw): '$CITY'"

if [ -z "$CITY" ]; then
    # Try to find the company line and extract city from it
    COMPANYLINE=$(grep -i "$MENTOR_EMPLOYER" kb/companies.md | head -1)
    echo "Company line: '$COMPANYLINE'"
    CITY=$(echo "$COMPANYLINE" | sed 's/.*[Hh]eadquarters[[:space:]]*[:=][[:space:]]*//' | sed 's/[[:space:]]*$//')
    echo "City (from line): '$CITY'"
fi

if [ -z "$CITY" ]; then
    echo "IMPOSSIBLE: Could not find headquarters city for $MENTOR_EMPLOYER"
    echo "IMPOSSIBLE" > answer.txt
    exit 0
fi

echo "Final answer: $CITY"
echo "$CITY" > answer.txt
echo "Answer written to answer.txt"
SCRIPT

bash solve.sh