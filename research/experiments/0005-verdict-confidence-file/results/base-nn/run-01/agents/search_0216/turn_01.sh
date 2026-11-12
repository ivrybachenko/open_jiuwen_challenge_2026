# Find the id of the person named Alex Morgan from the CSV files
# The name "Alex Morgan" might be stored as "A. Morgan" in people_new.csv
# Let's search both files for "Alex Morgan" or "A. Morgan"

# First, check people_new.csv which has header id,display_name
grep -i "a\. morgan\|alex morgan" people_new.csv

# Also check people_old.csv which has header id,name
grep -i "a\. morgan\|alex morgan" people_old.csv