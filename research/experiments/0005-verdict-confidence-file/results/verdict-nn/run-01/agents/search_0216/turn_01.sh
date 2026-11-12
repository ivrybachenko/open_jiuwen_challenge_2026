# Find the id of the person named Alex Morgan from the CSV files
# The name "Alex Morgan" might be stored as "A. Morgan" in people_new.csv
# Let's search both files for "Alex Morgan" or "A. Morgan"

# First, let's look at the content of both files to understand the data
echo "=== people_old.csv ==="
cat people_old.csv
echo ""
echo "=== people_new.csv ==="
cat people_new.csv

# Search for "Alex Morgan" or "A. Morgan" in both files
echo ""
echo "=== Searching for Alex Morgan ==="
grep -i "alex morgan\|a\. morgan" people_old.csv people_new.csv

# Based on the grep output, extract the id
# Let's find the line containing "A. Morgan" or "Alex Morgan" and extract the id
ID=$(grep -i "alex morgan\|a\. morgan" people_old.csv people_new.csv | head -1 | cut -d',' -f1)

echo ""
echo "=== Found ID: $ID ==="

# Write the answer to answer.txt
echo "$ID" > answer.txt

# Verify the answer
echo "Answer written to answer.txt:"
cat answer.txt