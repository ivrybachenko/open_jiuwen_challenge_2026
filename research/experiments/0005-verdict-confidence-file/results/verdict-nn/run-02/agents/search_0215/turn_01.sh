cat << 'EOF'
Let's break down the task:
1. Find Lena Ortiz in kb/people.md
2. Find her mentor
3. Find the employer of that mentor
4. Find the headquarters city of that employer in kb/companies.md
5. Write the city name to answer.txt

Let's start by examining the files.
EOF

# First, let's look at the people file to find Lena Ortiz and her mentor
echo "=== People File ==="
cat kb/people.md

echo ""
echo "=== Companies File ==="
cat kb/companies.md