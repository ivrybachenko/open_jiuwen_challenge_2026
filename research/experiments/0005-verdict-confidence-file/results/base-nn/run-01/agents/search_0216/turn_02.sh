# Find the id of the person named Alex Morgan from the CSV files
# Both files show id u-17 for A. Morgan / Alex Morgan
# Extract the id from the matching line

# Search both files and extract the id field
id=$(grep -i "a\. morgan\|alex morgan" people_new.csv people_old.csv | head -1 | cut -d',' -f1)

# Write the answer
echo "$id" > answer.txt
cat answer.txt