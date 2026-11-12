cat > brackets.py << 'EOF'
def balanced(text):
    stack = []
    matching = {')': '(', ']': '[', '}': '{'}
    opening = set('([{')
    closing = set(')]}')
    
    for char in text:
        if char in opening:
            stack.append(char)
        elif char in closing:
            if not stack or stack[-1] != matching[char]:
                return False
            stack.pop()
    
    return len(stack) == 0
EOF

python3 test_brackets.py && echo "DONE" > answer.txt