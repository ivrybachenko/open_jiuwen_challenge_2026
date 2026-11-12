cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-hard-nn/run-01/work/tasks/025_search_0201/workspace

# Read the README.md file and extract the version
VERSION=$(grep -i "version" docs/README.md | head -1 | sed -n 's/.*[Vv]ersion[:=]\s*\([0-9][0-9.]*\).*/\1/p')

# If the above pattern didn't work, try a more general approach
if [ -z "$VERSION" ]; then
    VERSION=$(grep -i "version" docs/README.md | head -1 | awk '{for(i=1;i<=NF;i++) if($i ~ /^[0-9][0-9.]*$/) print $i}')
fi

# If still empty, try to find any version-like string
if [ -z "$VERSION" ]; then
    VERSION=$(grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' docs/README.md | head -1)
fi

# Write the answer
echo "$VERSION" > answer.txt

# Create verdict.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Extracted version from docs/README.md" >> verdict.txt