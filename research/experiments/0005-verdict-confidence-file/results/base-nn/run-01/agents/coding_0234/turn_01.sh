cat > program.py << 'EOF'
import sys

def main():
    # Read the expression from stdin or from a file
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            expression = f.read().strip()
    else:
        expression = sys.stdin.read().strip()
    
    # Evaluate the expression safely
    # Since we need to handle +, -, * and parentheses with non-negative integers,
    # we can use Python's eval with a restricted environment.
    # However, to be safe and avoid any security issues, we can parse it ourselves.
    # But given the constraints (non-negative integers, +, -, *, parentheses),
    # and that intermediate values are non-negative, we can use eval with a safe namespace.
    
    # Let's use a simple recursive descent parser to be completely safe.
    
    def parse_expression(tokens, pos):
        """Parse addition and subtraction (lowest precedence)."""
        left, pos = parse_term(tokens, pos)
        while pos < len(tokens) and tokens[pos] in ('+', '-'):
            op = tokens[pos]
            pos += 1
            right, pos = parse_term(tokens, pos)
            if op == '+':
                left = left + right
            else:
                left = left - right
        return left, pos
    
    def parse_term(tokens, pos):
        """Parse multiplication (higher precedence)."""
        left, pos = parse_factor(tokens, pos)
        while pos < len(tokens) and tokens[pos] == '*':
            pos += 1
            right, pos = parse_factor(tokens, pos)
            left = left * right
        return left, pos
    
    def parse_factor(tokens, pos):
        """Parse numbers and parenthesized expressions."""
        if pos < len(tokens):
            token = tokens[pos]
            if token == '(':
                pos += 1  # skip '('
                value, pos = parse_expression(tokens, pos)
                if pos < len(tokens) and tokens[pos] == ')':
                    pos += 1  # skip ')'
                return value, pos
            elif token.isdigit():
                value = int(token)
                pos += 1
                return value, pos
        raise ValueError(f"Unexpected token at position {pos}: {tokens[pos] if pos < len(tokens) else 'EOF'}")
    
    # Tokenize the expression
    # We need to handle spaces, numbers, operators, and parentheses
    tokens = []
    i = 0
    while i < len(expression):
        if expression[i].isspace():
            i += 1
            continue
        elif expression[i] in ('+', '-', '*', '('):
            tokens.append(expression[i])
            i += 1
        elif expression[i] == ')':
            tokens.append(')')
            i += 1
        elif expression[i].isdigit():
            j = i
            while j < len(expression) and expression[j].isdigit():
                j += 1
            tokens.append(expression[i:j])
            i = j
        else:
            raise ValueError(f"Unexpected character: {expression[i]}")
    
    if not tokens:
        print(0)
        return
    
    result, pos = parse_expression(tokens, 0)
    if pos != len(tokens):
        raise ValueError(f"Unexpected tokens at end: {tokens[pos:]}")
    
    print(result)

if __name__ == '__main__':
    main()
EOF

echo "DONE" > answer.txt