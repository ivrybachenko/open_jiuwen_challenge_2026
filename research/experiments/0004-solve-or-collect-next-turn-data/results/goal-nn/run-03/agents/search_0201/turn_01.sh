cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-03/work/tasks/025_search_0201/workspace

# Extract the version from docs/README.md
VERSION=$(grep -i 'version' docs/README.md | head -1 | sed -n 's/.*[Vv]ersion[:=]\s*\([0-9][0-9.]*\).*/\1/p')

# If the above didn't work, try a more general approach
if [ -z "$VERSION" ]; then
    VERSION=$(grep -i 'version' docs/README.md | head -1 | awk '{print $NF}' | sed 's/[^0-9.]//g')
fi

# If still empty, just grab the first line that looks like it has a version
if [ -z "$VERSION" ]; then
    VERSION=$(cat docs/README.md | grep -i version | head -1)
fi

echo "Extracted version: $VERSION"
echo "$VERSION" > answer.txt
cat answer.txt