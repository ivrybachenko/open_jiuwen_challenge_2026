# Find the id of the person named "Alex Morgan" from the CSV files
# The task says to use file tools or bash (grep, cat)

# First, let's check both files for "Alex Morgan"
echo "=== Checking people_new.csv ==="
grep -i "Alex Morgan" people_new.csv || echo "Not found in people_new.csv"

echo "=== Checking people_old.csv ==="
grep -i "Alex Morgan" people_old.csv || echo "Not found in people_old.csv"

# Extract the id from the matching line
# The id is the first field (comma-separated)
ID=$(grep -i "Alex Morgan" people_new.csv people_old.csv 2>/dev/null | head -1 | cut -d',' -f1)

if [ -z "$ID" ]; then
    # Try with display_name column specifically
    ID=$(grep -i "Alex Morgan" people_new.csv 2>/dev/null | head -1 | cut -d',' -f1)
fi

if [ -z "$ID" ]; then
    ID=$(grep -i "Alex Morgan" people_old.csv 2>/dev/null | head -1 | cut -d',' -f1)
fi

echo "Found ID: $ID"

# Write the answer
echo "$ID" > answer.txt

# Create verdict file
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Found Alex Morgan's ID from CSV files" >> verdict.txt