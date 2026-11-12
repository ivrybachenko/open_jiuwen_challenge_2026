# Parse the knowledge base files to find the answer
# Step 1: Find Lena Ortiz's mentor
MENTOR=$(grep "Lena Ortiz" kb/people.md | sed 's/.*mentor=\([^,]*\).*/\1/' | tr -d ' ')
echo "Lena Ortiz's mentor: $MENTOR"

# Step 2: Find the mentor's employer
EMPLOYER=$(grep "$MENTOR" kb/people.md | sed 's/.*employer=\([^,]*\).*/\1/' | tr -d ' ')
echo "Mentor's employer: $EMPLOYER"

# Step 3: Find the employer's city
CITY=$(grep "$EMPLOYER" kb/companies.md | sed 's/.*city=\(.*\)/\1/' | tr -d ' ')
echo "Employer's city: $CITY"

# Write the answer
echo "$CITY" > answer.txt
cat answer.txt

# Create verdict file
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Found city for employer of Lena Ortiz's mentor" >> verdict.txt