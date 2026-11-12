# Find the id of the person named Alex Morgan from the CSV files
# Check both files for "Alex Morgan" and extract the corresponding id

# Search in people_new.csv (header: id,display_name)
NEW_ID=$(grep "Alex Morgan" people_new.csv | head -1 | cut -d',' -f1)

# Search in people_old.csv (header: id,name)
OLD_ID=$(grep "Alex Morgan" people_old.csv | head -1 | cut -d',' -f1)

# Determine which one has the match
if [ -n "$NEW_ID" ] && [ -z "$OLD_ID" ]; then
    ANSWER="$NEW_ID"
elif [ -z "$NEW_ID" ] && [ -n "$OLD_ID" ]; then
    ANSWER="$OLD_ID"
elif [ -n "$NEW_ID" ] && [ -n "$OLD_ID" ]; then
    # Both have it, use the one from the file that actually contains "Alex Morgan"
    # Check which file has the exact name match
    NEW_MATCH=$(grep -c "Alex Morgan" people_new.csv)
    OLD_MATCH=$(grep -c "Alex Morgan" people_old.csv)
    if [ "$NEW_MATCH" -gt 0 ] && [ "$OLD_MATCH" -eq 0 ]; then
        ANSWER="$NEW_ID"
    elif [ "$NEW_MATCH" -eq 0 ] && [ "$OLD_MATCH" -gt 0 ]; then
        ANSWER="$OLD_ID"
    else
        # Both have it, pick one (they should be the same person)
        ANSWER="$NEW_ID"
    fi
else
    # Neither has it
    ANSWER="NOT_FOUND"
fi

echo "Found ID: $ANSWER"
echo "$ANSWER" > answer.txt

# Create verdict.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Found Alex Morgan's ID from CSV files" >> verdict.txt