cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/base-nn/run-04/work/tasks/027_search_0215/workspace

# First, find Lena Ortiz's mentor from kb/people.md
mentor=$(grep -A 5 "Lena Ortiz" kb/people.md | grep -i "mentor" | head -1 | sed 's/.*mentor[[:space:]]*[:=-][[:space:]]*//i' | sed 's/[[:space:]]*$//')
echo "Mentor of Lena Ortiz: '$mentor'"

# Find Lena Ortiz's employer from kb/people.md
employer=$(grep -A 5 "Lena Ortiz" kb/people.md | grep -i "employer" | head -1 | sed 's/.*employer[[:space:]]*[:=-][[:space:]]*//i' | sed 's/[[:space:]]*$//')
echo "Employer of Lena Ortiz: '$employer'"

# Now find the mentor's employer
mentor_employer=$(grep -A 5 "$mentor" kb/people.md | grep -i "employer" | head -1 | sed 's/.*employer[[:space:]]*[:=-][[:space:]]*//i' | sed 's/[[:space:]]*$//')
echo "Employer of mentor: '$mentor_employer'"

# Find the headquarters city of the mentor's employer from kb/companies.md
city=$(grep -A 5 "$mentor_employer" kb/companies.md | grep -i "headquarters" | head -1 | sed 's/.*headquarters[[:space:]]*[:=-][[:space:]]*//i' | sed 's/[[:space:]]*$//')
echo "City: '$city'"

echo "$city" > answer.txt
cat answer.txt