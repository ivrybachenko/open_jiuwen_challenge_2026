cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-nn/run-02/work/tasks/025_search_0201/workspace

# Extract version from docs/README.md
VERSION=$(grep -iE 'version' docs/README.md | head -1 | sed -n 's/.*[Vv]ersion[:= ]*\([0-9][0-9.]*\).*/\1/p')

# If the above didn't work, try a more general approach
if [ -z "$VERSION" ]; then
    VERSION=$(grep -iE 'version' docs/README.md | head -1 | grep -oE '[0-9]+(\.[0-9]+)*' | head -1)
fi

# Write the answer
echo "$VERSION" > answer.txt
cat answer.txt