# Find the file that mentions Sergei Garcia and extract the city from it
grep -l "Sergei Garcia" kb/*.md | xargs grep -i "headquarters\|city\|location" | head -5