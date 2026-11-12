cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-03/work/tasks/025_search_0201/workspace

# First, let's see the full content of the README to understand its format
cat docs/README.md

# Then extract the version - we'll try multiple patterns
VERSION=$(cat docs/README.md | grep -iE '(version|ver)\s*[:=]?' | head -1 | sed 's/.*[Vv]ersion[:=]\s*//i' | sed 's/[[:space:]]*$//' | sed 's/[^0-9.].*//')

# If that didn't work, try to find any version-like string (e.g., 1.2.3)
if [ -z "$VERSION" ]; then
    VERSION=$(cat docs/README.md | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1)
fi

# If still empty, try to get the first line that mentions version
if [ -z "$VERSION" ]; then
    VERSION=$(cat docs/README.md | grep -i version | head -1)
fi

echo "Extracted version: '$VERSION'"
echo "$VERSION" > answer.txt
cat answer.txt