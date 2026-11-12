# Find the id of the person named Alex Morgan from the CSV files
# The name "Alex Morgan" might be stored as "A. Morgan" in people_new.csv
# Let's search both files for any row containing "Alex Morgan" or "A. Morgan"

# First, let's look at the content of both files to understand the data
echo "=== people_old.csv ==="
cat people_old.csv
echo ""
echo "=== people_new.csv ==="
cat people_new.csv

# Search for Alex Morgan or A. Morgan in both files
echo ""
echo "=== Searching for Alex Morgan ==="
grep -i "alex morgan" people_old.csv people_new.csv || echo "No exact match for 'Alex Morgan'"

echo ""
echo "=== Searching for A. Morgan ==="
grep -i "a\. morgan" people_old.csv people_new.csv || echo "No exact match for 'A. Morgan'"

# Extract the id from the matching line
# Check people_new.csv for A. Morgan
ID=$(grep -i "a\. morgan" people_new.csv | head -1 | cut -d',' -f1)
if [ -z "$ID" ]; then
    # Check people_old.csv for Alex Morgan
    ID=$(grep -i "alex morgan" people_old.csv | head -1 | cut -d',' -f1)
fi

echo ""
echo "=== Found ID: $ID ==="

# Write the answer
echo "$ID" > answer.txt
echo "Answer written to answer.txt"
cat answer.txt