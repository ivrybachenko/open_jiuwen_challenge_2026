cat > program.py << 'EOF'
import sys

def parse_expression(s):
    """Parse and evaluate an arithmetic expression with +, -, * and parentheses."""
    s = s.strip()
    if not s:
        raise ValueError("Empty expression")
    
    pos = [0]  # Use list to allow mutation in nested functions
    
    def peek():
        if pos[0] < len(s):
            return s[pos[0]]
        return None
    
    def consume():
        ch = s[pos[0]]
        pos[0] += 1
        return ch
    
    def skip_spaces():
        while pos[0] < len(s) and s[pos[0]] == ' ':
            pos[0] += 1
    
    def parse_term():
        """Parse a term (factors multiplied/divided)."""
        skip_spaces()
        val = parse_factor()
        
        while True:
            skip_spaces()
            if pos[0] < len(s) and s[pos[0]] == '*':
                consume()
                skip_spaces()
                right = parse_factor()
                val = val * right
            else:
                break
        return val
    
    def parse_factor():
        """Parse a factor (number or parenthesized expression)."""
        skip_spaces()
        ch = peek()
        
        if ch == '(':
            consume()  # consume '('
            val = parse_expression_internal()
            skip_spaces()
            if peek() == ')':
                consume()  # consume ')'
            else:
                raise ValueError("Missing closing parenthesis")
            return val
        elif ch.isdigit():
            start = pos[0]
            while pos[0] < len(s) and s[pos[0]].isdigit():
                pos[0] += 1
            return int(s[start:pos[0]])
        else:
            raise ValueError(f"Unexpected character: {ch}")
    
    def parse_expression_internal():
        """Parse an expression with + and - operators."""
        val = parse_term()
        
        while True:
            skip_spaces()
            if pos[0] < len(s) and s[pos[0]] == '+':
                consume()
                skip_spaces()
                right = parse_term()
                val = val + right
            elif pos[0] < len(s) and s[pos[0]] == '-':
                consume()
                skip_spaces()
                right = parse_term()
                val = val - right
            else:
                break
        return val
    
    result = parse_expression_internal()
    skip_spaces()
    if pos[0] != len(s):
        raise ValueError(f"Unexpected character at position {pos[0]}: {s[pos[0]]}")
    
    return result

if __name__ == "__main__":
    expression = sys.stdin.read().strip()
    if not expression:
        raise ValueError("No input provided")
    result = parse_expression(expression)
    print(result)
EOF

echo "DONE" > answer.txt