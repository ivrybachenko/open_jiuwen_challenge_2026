cat > vowels.py << 'EOF'
def count_vowels(text):
    """Count the number of vowels (a, e, i, o, u) in the given text, case-insensitive.
    Does not count 'y' as a vowel."""
    vowels = set('aeiouAEIOU')
    count = 0
    for char in text:
        if char in vowels:
            count += 1
    return count
EOF

python3 test_vowels.py