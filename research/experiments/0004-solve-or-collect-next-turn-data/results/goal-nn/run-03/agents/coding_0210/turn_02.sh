cat > brackets.py << 'EOF'
def balanced(text):
    """
    Return True when every opening bracket has a matching closing bracket
    of the same kind and brackets are properly nested.
    The kinds are (), [], and {}. Ignore all other characters.
    """
    stack = []
    matching = {')': '(', ']': '[', '}': '{'}
    
    for char in text:
        if char in '([{':
            stack.append(char)
        elif char in ')]}':
            if not stack or stack[-1] != matching[char]:
                return False
            stack.pop()
    
    return len(stack) == 0
EOF

python3 test_brackets.py && echo "DONE" > answer.txt