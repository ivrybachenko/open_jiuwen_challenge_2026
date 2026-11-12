# Step 1: Find Lena Ortiz's mentor from kb/people.md
# Step 2: Find the mentor's employer from kb/people.md
# Step 3: Find the headquarters city of that employer from kb/companies.md

# Extract Lena Ortiz's mentor
MENTOR=$(grep -A1 "Lena Ortiz" kb/people.md | grep "mentor=" | sed 's/.*mentor=\([^,]*\).*/\1/' | tr -d ' ')
echo "Mentor of Lena Ortiz: $MENTOR"

# Extract the mentor's employer
EMPLOYER=$(grep -A1 "$MENTOR" kb/people.md | grep "employer=" | sed 's/.*employer=\([^,]*\).*/\1/' | tr -d ' ')
echo "Employer of $MENTOR: $EMPLOYER"

# Extract the city for that employer from kb/companies.md
CITY=$(grep -A1 "$EMPLOYER" kb/companies.md | grep "city=" | sed 's/.*city=\([^,]*\).*/\1/' | tr -d ' ')
echo "City: $CITY"

# Write the answer
echo "$CITY" > answer.txt
cat answer.txt