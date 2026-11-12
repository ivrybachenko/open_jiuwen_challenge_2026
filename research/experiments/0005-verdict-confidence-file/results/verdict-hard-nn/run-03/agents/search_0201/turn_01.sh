# Extract the version from docs/README.md and write it to answer.txt
grep -i 'version' docs/README.md | head -1 | sed 's/.*[Vv]ersion[:= ]*//' | tr -d '[:space:]' > answer.txt

# Create verdict.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Extracted version from docs/README.md" >> verdict.txt