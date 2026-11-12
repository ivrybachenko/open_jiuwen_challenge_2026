# Find the file that mentions Sergei Garcia and extract the city
grep -l "Sergei Garcia" kb/*.md | head -1 | xargs cat | grep -i "city\|headquarters\|location\|based in" | head -5