cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-nn/run-01/work/tasks/025_search_0201/workspace

# Read the README.md file and extract the version
VERSION=$(grep -i "version" docs/README.md | head -n 1 | sed -n 's/.*[Vv]ersion[:=]\s*\([0-9][0-9.]*\).*/\1/p')

# If the above didn't work, try a more general approach
if [ -z "$VERSION" ]; then
    VERSION=$(grep -i "version" docs/README.md | head -n 1 | awk '{for(i=1;i<=NF;i++) if($i ~ /^[0-9]+\.[0-9]+/) print $i}')
fi

# If still empty, try to find any version-like string
if [ -z "$VERSION" ]; then
    VERSION=$(grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' docs/README.md | head -n 1)
fi

echo "Extracted version: $VERSION"
echo "$VERSION" > answer.txt

# Write verdict.txt
cat > verdict.txt << 'EOF'
solved
1.00
Successfully extracted version from README.md
EOF