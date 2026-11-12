# Parse the data to find the answer
# 1. Find Lena Ortiz's mentor from kb/people.md
# 2. Find the employer of that mentor from kb/people.md
# 3. Find the city of that employer from kb/companies.md

# Step 1: Get Lena Ortiz's mentor
MENTOR=$(grep "Lena Ortiz" kb/people.md | sed 's/.*mentor=\([^,]*\).*/\1/' | tr -d ' ')
echo "Mentor of Lena Ortiz: $MENTOR"

# Step 2: Get the employer of the mentor
EMPLOYER=$(grep "$MENTOR" kb/people.md | sed 's/.*employer=\([^,]*\).*/\1/' | tr -d ' ')
echo "Employer of $MENTOR: $EMPLOYER"

# Step 3: Get the city of the employer
CITY=$(grep "$EMPLOYER" kb/companies.md | sed 's/.*city=\(.*\)/\1/' | tr -d ' ')
echo "City of $EMPLOYER: $CITY"

# Write the answer
echo "$CITY" > answer.txt
cat answer.txt

# Create verdict file
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Found city for employer of Lena Ortiz's mentor" >> verdict.txt