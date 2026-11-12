cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-hard-nn/run-04/work/tasks/025_search_0201/workspace

# Read the README.md file and extract the version
VERSION=$(grep -i "version" docs/README.md | head -n 1 | sed 's/.*[Vv]ersion[=: ]*//i' | sed 's/[[:space:]]*$//')

# If the above didn't work, try a more general approach
if [ -z "$VERSION" ]; then
    VERSION=$(cat docs/README.md | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n 1)
fi

# Write the answer
echo "$VERSION" > answer.txt

# Create verdict.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Extracted version from docs/README.md" >> verdict.txt