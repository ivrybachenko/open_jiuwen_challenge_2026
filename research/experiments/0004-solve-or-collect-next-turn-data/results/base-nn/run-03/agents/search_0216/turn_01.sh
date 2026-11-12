# Find the id of the person named Alex Morgan from the CSV files
# Check both files for "Alex Morgan" and extract the corresponding id

# Check people_new.csv (header: id,display_name)
NEW_ID=$(grep "Alex Morgan" people_new.csv | cut -d',' -f1)

# Check people_old.csv (header: id,name)
OLD_ID=$(grep "Alex Morgan" people_old.csv | cut -d',' -f1)

# Determine which one has the match
if [ -n "$NEW_ID" ]; then
    echo "$NEW_ID" > answer.txt
elif [ -n "$OLD_ID" ]; then
    echo "$OLD_ID" > answer.txt
else
    echo "Not found" > answer.txt
fi