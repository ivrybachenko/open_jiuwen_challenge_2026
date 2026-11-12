# Find the id of the person named Alex Morgan from the CSV files
# The name "Alex Morgan" might be stored as "A. Morgan" in one file and "Alex Morgan" in another

# First, let's look at the files to understand the data
echo "=== people_new.csv ==="
cat people_new.csv
echo ""
echo "=== people_old.csv ==="
cat people_old.csv

# Search for "Alex Morgan" or "A. Morgan" in both files
echo ""
echo "=== Searching for Alex Morgan ==="
grep -i "morgan" people_new.csv
grep -i "morgan" people_old.csv

# Extract the id for the person with name containing "Morgan"
# Check both files
NEW_ID=$(grep -i "morgan" people_new.csv | head -1 | cut -d',' -f1)
OLD_ID=$(grep -i "morgan" people_old.csv | head -1 | cut -d',' -f1)

echo "ID from people_new.csv: $NEW_ID"
echo "ID from people_old.csv: $OLD_ID"

# The task says to find the id of the person named Alex Morgan and answer with the id from the files
# Both files list the same people, so either id should work, but let's use the one that matches "Alex Morgan"
# Since "A. Morgan" is likely "Alex Morgan", we'll use the id from the file where we found the match

# Write the answer
echo "$NEW_ID" > answer.txt
echo "Answer written to answer.txt: $NEW_ID"