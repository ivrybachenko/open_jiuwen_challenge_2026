# Find the file that mentions Sergei Garcia and extract the company name
company=$(grep -l "Sergei Garcia" kb/*.md | head -1)
echo "Found Sergei Garcia in: $company"

# Extract the company name from the file
# Look for patterns like "Company: X" or "Name: X" or just the company name
company_name=$(grep -i "company\|employer\|works at\|works for" "$company" | head -5)
echo "Company info: $company_name"

# Let's look at the content of the file to understand the structure
cat "$company"

# Now find the company's KB file and extract the city
# First, let's find which company file corresponds to Sergei Garcia's employer
# We need to find the company name first, then look it up in the kb files

# Let's grep for the company name in other kb files to find the headquarters city
# First, let's see what's in the file with Sergei Garcia
echo "---"
echo "Full content of the file with Sergei Garcia:"
cat "$company"