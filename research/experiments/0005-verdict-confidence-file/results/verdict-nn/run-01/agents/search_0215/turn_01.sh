cat << 'EOF'
Let's break down the task:
1. Find Lena Ortiz in kb/people.md
2. Find her mentor
3. Find the employer of that mentor
4. Find the headquarters city of that employer in kb/companies.md

Let's start by reading the files.
EOF

# Read people.md to find Lena Ortiz and her mentor
cat kb/people.md

echo "---"

# Read companies.md to find headquarters cities
cat kb/companies.md