cat > vowels.py << 'EOF'
def count_vowels(text):
    return sum(1 for c in text.lower() if c in 'aeiou')
EOF

python3 test_vowels.py
echo "DONE" > answer.txt