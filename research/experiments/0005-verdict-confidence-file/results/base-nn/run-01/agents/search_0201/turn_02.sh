cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/base-nn/run-01/work/tasks/025_search_0201/workspace

# First, let's see what's in the README
cat docs/README.md

# Extract version - try multiple patterns
VERSION=$(cat docs/README.md | grep -iE 'version' | head -1 | sed 's/.*[Vv]ersion[: ]*//i' | grep -oE '[0-9]+(\.[0-9]+)*' | head -1)

# If still empty, try to get any version-like string from the file
if [ -z "$VERSION" ]; then
    VERSION=$(cat docs/README.md | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
fi

# If still empty, try to get any version-like string (e.g., v1.2.3)
if [ -z "$VERSION" ]; then
    VERSION=$(cat docs/README.md | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' | head -1 | sed 's/^v//')
fi

# Write the answer
echo "$VERSION" > answer.txt
echo "Answer written: $VERSION"
cat answer.txt