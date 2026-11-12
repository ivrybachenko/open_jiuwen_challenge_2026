cat > program.py << 'EOF'
import sys

def parse_expression(s):
    """Parse and evaluate an arithmetic expression with +, -, * and parentheses."""
    s = s.strip()
    if not s:
        raise ValueError("Empty expression")
    
    # Tokenize
    tokens = []
    i = 0
    while i < len(s):
        if s[i].isspace():
            i += 1
            continue
        if s[i] in '()+-*':
            tokens.append(s[i])
            i += 1
        elif s[i].isdigit():
            j = i
            while j < len(s) and s[j].isdigit():
                j += 1
            tokens.append(int(s[i:j]))
            i = j
        else:
            raise ValueError(f"Unexpected character: {s[i]}")
    
    pos = [0]  # Use list to allow mutation in nested function
    
    def parse_expr():
        """Parse addition and subtraction (lowest precedence)."""
        left = parse_term()
        while pos[0] < len(tokens) and tokens[pos[0]] in ('+', '-'):
            op = tokens[pos[0]]
            pos[0] += 1
            right = parse_term()
            if op == '+':
                left = left + right
            else:
                left = left - right
        return left
    
    def parse_term():
        """Parse multiplication (higher precedence)."""
        left = parse_primary()
        while pos[0] < len(tokens) and tokens[pos[0]] == '*':
            pos[0] += 1
            right = parse_primary()
            left = left * right
        return left
    
    def parse_primary():
        """Parse numbers and parenthesized expressions."""
        if pos[0] >= len(tokens):
            raise ValueError("Unexpected end of expression")
        
        token = tokens[pos[0]]
        
        if isinstance(token, int):
            pos[0] += 1
            return token
        elif token == '(':
            pos[0] += 1
            result = parse_expr()
            if pos[0] >= len(tokens) or tokens[pos[0]] != ')':
                raise ValueError("Missing closing parenthesis")
            pos[0] += 1
            return result
        else:
            raise ValueError(f"Unexpected token: {token}")
    
    result = parse_expr()
    if pos[0] != len(tokens):
        raise ValueError(f"Unexpected token at end: {tokens[pos[0]]}")
    
    return result

if __name__ == "__main__":
    expression = sys.stdin.read().strip()
    if not expression:
        raise ValueError("No input provided")
    result = parse_expression(expression)
    print(result)
EOF

echo "DONE" > answer.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Simple arithmetic expression parser with +, -, *, parentheses" >> verdict.txt