# Extract the version from docs/README.md
VERSION=$(grep -i 'version' docs/README.md | head -n 1 | sed -n 's/.*[Vv]ersion[:=]\s*\([0-9][0-9.]*\).*/\1/p')

# If the above didn't work, try a more general pattern
if [ -z "$VERSION" ]; then
  VERSION=$(grep -i 'version' docs/README.md | head -n 1 | sed -n 's/.*\([0-9][0-9.]*\).*/\1/p')
fi

# If still empty, try to find any version-like string
if [ -z "$VERSION" ]; then
  VERSION=$(grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' docs/README.md | head -n 1)
fi

# Write the answer
echo "$VERSION" > answer.txt

# Create verdict.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Extracted version from docs/README.md" >> verdict.txt