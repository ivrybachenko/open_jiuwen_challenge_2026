cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/base-nn/run-02/work/tasks/027_search_0215/workspace

# Step 1: Find Lena Ortiz's mentor from kb/people.md
mentor=$(grep -A 5 "Lena Ortiz" kb/people.md | grep -i "mentor" | head -1 | sed 's/.*mentor[[:space:]]*[:=][[:space:]]*//' | sed 's/[[:space:]]*$//')
echo "Mentor of Lena Ortiz: '$mentor'"

# Step 2: Find Lena Ortiz's employer from kb/people.md
employer=$(grep -A 5 "Lena Ortiz" kb/people.md | grep -i "employer" | head -1 | sed 's/.*employer[[:space:]]*[:=][[:space:]]*//' | sed 's/[[:space:]]*$//')
echo "Employer of Lena Ortiz: '$employer'"

# Step 3: Find the headquarters city of the mentor's employer from kb/companies.md
# First, find the employer of the mentor
mentor_employer=$(grep -A 5 "$mentor" kb/people.md | grep -i "employer" | head -1 | sed 's/.*employer[[:space:]]*[:=][[:space:]]*//' | sed 's/[[:space:]]*$//')
echo "Employer of mentor ($mentor): '$mentor_employer'"

# Step 4: Find the headquarters city of that employer from kb/companies.md
city=$(grep -A 5 "$mentor_employer" kb/companies.md | grep -i "headquarters" | head -1 | sed 's/.*headquarters[[:space:]]*[:=][[:space:]]*//' | sed 's/[[:space:]]*$//')
echo "City: '$city'"

# Write the answer
echo "$city" > answer.txt
cat answer.txt