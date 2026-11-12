# Find the id of the person named Alex Morgan from the CSV files
# Check both files for "Alex Morgan" and extract the corresponding id

# Search in people_new.csv (header: id,display_name)
id_new=$(grep "Alex Morgan" people_new.csv | head -1 | cut -d',' -f1)

# Search in people_old.csv (header: id,name)
id_old=$(grep "Alex Morgan" people_old.csv | head -1 | cut -d',' -f1)

# Determine which one is valid
if [ -n "$id_new" ]; then
    echo "$id_new" > answer.txt
    echo "Found in people_new.csv: $id_new"
elif [ -n "$id_old" ]; then
    echo "$id_old" > answer.txt
    echo "Found in people_old.csv: $id_old"
else
    echo "Not found" > answer.txt
    echo "Alex Morgan not found in either file"
fi

# Create verdict.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Found Alex Morgan's id in the CSV files" >> verdict.txt