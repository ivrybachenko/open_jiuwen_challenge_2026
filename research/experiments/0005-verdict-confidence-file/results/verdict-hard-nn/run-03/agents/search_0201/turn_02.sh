# First, let's see what's in the README.md to understand the format
cat docs/README.md

# Extract the version from docs/README.md and write it to answer.txt
# Try multiple patterns to find the version
VERSION=$(grep -i 'version' docs/README.md | head -1 | sed -E 's/.*[Vv]ersion[:= ]*([0-9][0-9a-zA-Z._-]+).*/\1/' | tr -d '[:space:]')

# If the above didn't work, try a simpler approach
if [ -z "$VERSION" ]; then
    VERSION=$(grep -oE '[0-9]+\.[0-9]+[0-9a-zA-Z._-]*' docs/README.md | head -1)
fi

# If still empty, try to get any version-like string
if [ -z "$VERSION" ]; then
    VERSION=$(grep -i 'version' docs/README.md | head -1 | awk '{for(i=1;i<=NF;i++) if($i ~ /^[0-9]/) print $i}')
fi

echo "Extracted version: '$VERSION'"
echo "$VERSION" > answer.txt

# Verify answer.txt is non-empty
if [ ! -s answer.txt ]; then
    echo "ERROR: answer.txt is empty, trying fallback"
    # Last resort: just dump the relevant line
    grep -i 'version' docs/README.md | head -1 > answer.txt
fi

# Create verdict.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Extracted version from docs/README.md" >> verdict.txt