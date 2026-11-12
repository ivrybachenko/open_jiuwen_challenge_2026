cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-04/work/tasks/027_search_0215/workspace

# The system grep doesn't support -P (Perl regex). Let's first inspect the files to understand their format.
echo "=== kb/people.md ==="
cat kb/people.md
echo ""
echo "=== kb/companies.md ==="
cat kb/companies.md

# Now let's use awk or sed instead of grep -P
# Step 1: Find Lena Ortiz's mentor
mentor_name=$(awk '/[Ll]ena [Oo]rtiz/{found=1} found && /mentor:/{gsub(/.*mentor: */, ""); print; exit}' kb/people.md)
echo "Mentor name: '$mentor_name'"

# Step 2: Find the mentor's employer
mentor_employer=$(awk -v name="$mentor_name" 'BEGIN{IGNORECASE=1} $0 ~ name {found=1} found && /employer:/{gsub(/.*employer: */, ""); print; exit}' kb/people.md)
echo "Mentor's employer: '$mentor_employer'"

# Step 3: Find the headquarters city of that employer
city=$(awk -v name="$mentor_employer" 'BEGIN{IGNORECASE=1} $0 ~ name {found=1} found && /headquarters:/{gsub(/.*headquarters: */, ""); print; exit}' kb/companies.md)
echo "City: '$city'"

# Write the answer
echo "$city" > answer.txt
echo "Answer written to answer.txt:"
cat answer.txt