# Sergei Garcia's employer is Fjord Data. Now find the city where Fjord Data is headquartered.
# Search for Fjord Data in the kb files to find the company file and extract the city.

# Find the company file for Fjord Data
company_file=$(grep -l "Fjord Data" kb/*.md | head -1)
echo "Company file: $company_file"

# Extract the city from the company file
# Look for patterns like "City:", "Headquarters:", "Location:", etc.
city=$(grep -iE "city|headquarters|location|based in" "$company_file" | head -5)
echo "City info: $city"

# Let's also cat the full file to be sure
echo "---"
cat "$company_file"

# Extract just the city name
city_name=$(grep -iE "city|headquarters|location|based in" "$company_file" | sed -E 's/.*[:\s]+//' | head -1 | tr -d '[:space:]')
echo "Extracted city: $city_name"

# Write the answer
echo "$city_name" > answer.txt
cat answer.txt