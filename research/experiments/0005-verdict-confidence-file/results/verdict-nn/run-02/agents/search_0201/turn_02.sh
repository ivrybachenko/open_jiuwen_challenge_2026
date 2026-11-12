cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-nn/run-02/work/tasks/025_search_0201/workspace

# First, let's see what's in the README
cat docs/README.md

# Extract version - try multiple patterns
VERSION=$(cat docs/README.md | grep -iE 'version' | head -5)
echo "=== Lines with version ==="
echo "$VERSION"

# Try to extract a version number
VER=$(cat docs/README.md | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)*' | head -1)
if [ -z "$VER" ]; then
    VER=$(cat docs/README.md | grep -oE 'v[0-9]+\.[0-9]+(\.[0-9]+)*' | head -1 | sed 's/^v//')
fi
if [ -z "$VER" ]; then
    VER="unknown"
fi

echo "Extracted version: $VER"
echo "$VER" > answer.txt
cat answer.txt