# Parse the task: Find the employer of the mentor of Lena Ortiz, then find the city where that employer is headquartered.

# Step 1: Find Lena Ortiz's mentor from kb/people.md
# From the output: "Lena Ortiz: mentor=Tom Reed, employer=Blue Harbor"
# So Lena Ortiz's mentor is Tom Reed.

# Step 2: Find Tom Reed's employer from kb/people.md
# From the output: "Tom Reed: employer=Northwind Labs"
# So Tom Reed's employer is Northwind Labs.

# Step 3: Find the city where Northwind Labs is headquartered from kb/companies.md
# From the output: "Northwind Labs: city=Lisbon"
# So the city is Lisbon.

echo "Lisbon" > answer.txt

# Create verdict.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Found mentor of Lena Ortiz (Tom Reed), his employer (Northwind Labs), and its city (Lisbon)" >> verdict.txt