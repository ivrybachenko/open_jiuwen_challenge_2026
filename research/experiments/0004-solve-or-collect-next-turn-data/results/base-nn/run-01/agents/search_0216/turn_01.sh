# Find the id of the person named Alex Morgan from the CSV files
# Check both files for "Alex Morgan" and extract the corresponding id

# Search in people_new.csv (header: id,display_name)
NEW_ID=$(grep -i "Alex Morgan" people_new.csv | head -1 | cut -d',' -f1)

# Search in people_old.csv (header: id,name)
OLD_ID=$(grep -i "Alex Morgan" people_old.csv | head -1 | cut -d',' -f1)

# Determine which one has the match
if [ -n "$NEW_ID" ] && [ -z "$OLD_ID" ]; then
    ANSWER="$NEW_ID"
elif [ -n "$OLD_ID" ] && [ -z "$NEW_ID" ]; then
    ANSWER="$OLD_ID"
elif [ -n "$NEW_ID" ] && [ -n "$OLD_ID" ]; then
    # Both have it, use the one that matches the name format better
    # Check if display_name contains "Alex Morgan" exactly or name contains it
    NEW_NAME=$(grep -i "Alex Morgan" people_new.csv | head -1 | cut -d',' -f2-)
    OLD_NAME=$(grep -i "Alex Morgan" people_old.csv | head -1 | cut -d',' -f2-)
    if echo "$NEW_NAME" | grep -qi "Alex Morgan"; then
        ANSWER="$NEW_ID"
    else
        ANSWER="$OLD_ID"
    fi
else
    ANSWER="NOT_FOUND"
fi

echo "Found ID: $ANSWER"
echo "$ANSWER" > answer.txt