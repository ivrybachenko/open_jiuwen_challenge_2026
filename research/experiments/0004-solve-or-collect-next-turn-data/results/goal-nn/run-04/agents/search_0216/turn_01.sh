# Find the id of the person named Alex Morgan from the CSV files
# Check both files for "Alex Morgan" and extract the corresponding id

# Search in people_new.csv (header: id,display_name)
id_new=$(grep -i "Alex Morgan" people_new.csv | head -1 | cut -d',' -f1)

# Search in people_old.csv (header: id,name)
id_old=$(grep -i "Alex Morgan" people_old.csv | head -1 | cut -d',' -f1)

# Determine which one has the match
if [ -n "$id_new" ]; then
    echo "Found in people_new.csv: $id_new"
    echo "$id_new" > answer.txt
elif [ -n "$id_old" ]; then
    echo "Found in people_old.csv: $id_old"
    echo "$id_old" > answer.txt
else
    echo "Alex Morgan not found in either file"
    echo "NOT_FOUND" > answer.txt
fi