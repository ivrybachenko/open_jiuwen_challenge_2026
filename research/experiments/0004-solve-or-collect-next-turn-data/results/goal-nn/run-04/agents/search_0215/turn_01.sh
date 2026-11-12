cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-04/work/tasks/027_search_0215/workspace

# First, find Lena Ortiz's mentor from kb/people.md
mentor=$(grep -i "Lena Ortiz" kb/people.md | grep -oP '(?<=mentor: ).*')
echo "Mentor of Lena Ortiz: $mentor"

# Now find Lena Ortiz's employer from kb/people.md
employer=$(grep -i "Lena Ortiz" kb/people.md | grep -oP '(?<=employer: ).*')
echo "Employer of Lena Ortiz: $employer"

# Wait, the question asks for: employer of the mentor of Lena Ortiz
# So I need:
# 1. Find Lena Ortiz's mentor
# 2. Find that mentor's employer
# 3. Find the headquarters city of that employer

# Step 1: Get mentor name
mentor_name=$(grep -i "Lena Ortiz" kb/people.md | grep -oP '(?<=mentor: ).*')
echo "Mentor name: $mentor_name"

# Step 2: Get the mentor's employer
mentor_employer=$(grep -i "$mentor_name" kb/people.md | grep -oP '(?<=employer: ).*')
echo "Mentor's employer: $mentor_employer"

# Step 3: Get the headquarters city of that employer from kb/companies.md
city=$(grep -i "$mentor_employer" kb/companies.md | grep -oP '(?<=headquarters: ).*')
echo "City: $city"

# Write the answer
echo "$city" > answer.txt
cat answer.txt