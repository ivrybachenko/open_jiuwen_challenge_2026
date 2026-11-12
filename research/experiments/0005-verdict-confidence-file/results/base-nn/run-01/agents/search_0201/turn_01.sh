cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/base-nn/run-01/work/tasks/025_search_0201/workspace

# Extract version from docs/README.md
VERSION=$(grep -iE 'version|v[0-9]' docs/README.md | head -1 | grep -oE '[0-9]+(\.[0-9]+)*' | head -1)

# If no version found, try to get any version-like string
if [ -z "$VERSION" ]; then
    VERSION=$(grep -iE 'version' docs/README.md | head -1 | sed 's/.*[Vv]ersion[: ]*//i' | grep -oE '[0-9]+(\.[0-9]+)*' | head -1)
fi

# Write the answer
echo "$VERSION" > answer.txt
cat answer.txt