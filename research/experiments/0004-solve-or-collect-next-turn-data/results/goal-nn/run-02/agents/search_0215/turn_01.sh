cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-02/work/tasks/027_search_0215/workspace

# First, find Lena Ortiz's mentor from kb/people.md
mentor=$(grep -A 5 "Lena Ortiz" kb/people.md | grep -i "mentor" | head -1 | sed 's/.*mentor[:\s]*//i' | sed 's/[,\s].*//')
echo "Mentor of Lena Ortiz: '$mentor'"

# Now find the employer of that mentor from kb/people.md
employer=$(grep -A 5 "$mentor" kb/people.md | grep -i "employer" | head -1 | sed 's/.*employer[:\s]*//i' | sed 's/[,\s].*//')
echo "Employer of $mentor: '$employer'"

# Now find the headquarters city of that employer from kb/companies.md
city=$(grep -A 5 "$employer" kb/companies.md | grep -i "headquarters" | head -1 | sed 's/.*headquarters[:\s]*//i' | sed 's/[,\s].*//')
echo "City: '$city'"

echo "$city" > answer.txt
cat answer.txt