# Step 1: Find Lena Ortiz's mentor from kb/people.md
# From the file: Lena Ortiz: mentor=Tom Reed, employer=Blue Harbor
# So Lena Ortiz's mentor is Tom Reed

# Step 2: Find the employer of Tom Reed
# From the file: Tom Reed: employer=Northwind Labs
# So the employer of Lena Ortiz's mentor is Northwind Labs

# Step 3: Find the headquarters city of Northwind Labs from kb/companies.md
# From the file: Northwind Labs: city=Lisbon
# So the city is Lisbon

echo "Lisbon" > answer.txt
cat answer.txt