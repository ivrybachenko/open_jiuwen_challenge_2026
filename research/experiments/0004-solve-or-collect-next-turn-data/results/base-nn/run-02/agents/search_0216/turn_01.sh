# Find the id of the person named Alex Morgan from the CSV files
# Check both files for "Alex Morgan" and extract the corresponding id

# First, check people_new.csv (header: id,display_name)
NEW_ID=$(grep "Alex Morgan" people_new.csv | cut -d',' -f1)

# If not found, check people_old.csv (header: id,name)
if [ -z "$NEW_ID" ]; then
    OLD_ID=$(grep "Alex Morgan" people_old.csv | cut -d',' -f1)
    if [ -n "$OLD_ID" ]; then
        echo "$OLD_ID" > answer.txt
        exit 0
    fi
else
    echo "$NEW_ID" > answer.txt
    exit 0
fi

# If not found in either file, write IMPOSSIBLE
echo "IMPOSSIBLE: Alex Morgan not found in either file" > answer.txt