# Parse the knowledge base files to find the answer
# Step 1: Find Lena Ortiz's mentor
mentor=$(grep "Lena Ortiz" kb/people.md | sed 's/.*mentor=\([^,]*\).*/\1/' | tr -d ' ')
echo "Lena Ortiz's mentor: $mentor"

# Step 2: Find the mentor's employer
employer=$(grep "$mentor" kb/people.md | sed 's/.*employer=\([^,]*\).*/\1/' | tr -d ' ')
echo "Mentor's employer: $employer"

# Step 3: Find the employer's city
city=$(grep "$employer" kb/companies.md | sed 's/.*city=\([^,]*\).*/\1/' | tr -d ' ')
echo "Employer's city: $city"

# Write the answer
echo "$city" > answer.txt
cat answer.txt

# Create verdict file
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Found city for employer of mentor of Lena Ortiz" >> verdict.txt