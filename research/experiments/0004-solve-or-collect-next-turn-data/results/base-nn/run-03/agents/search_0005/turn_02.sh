# Find the file that mentions Sergei Garcia and extract the city from it
grep -l "Sergei Garcia" kb/*.md | xargs grep -i "headquarters\|city\|based in\|located in" | head -5