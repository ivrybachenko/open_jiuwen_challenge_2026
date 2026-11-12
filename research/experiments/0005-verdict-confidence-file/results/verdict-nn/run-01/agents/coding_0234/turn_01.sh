cat > program.py << 'EOF'
import sys

def evaluate(expr):
    # Remove all spaces
    expr = expr.replace(' ', '')
    
    # Tokenize
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]
        if c.isdigit():
            j = i
            while j < len(expr) and expr[j].isdigit():
                j += 1
            tokens.append(('NUM', int(expr[i:j])))
            i = j
        elif c in '+-*()':
            tokens.append(('OP', c))
            i += 1
        else:
            raise ValueError(f"Unexpected character: {c}")
    
    # Parse and evaluate using recursive descent
    pos = [0]
    
    def parse_expr():
        """Parse addition and subtraction (lowest precedence)"""
        left = parse_term()
        while pos[0] < len(tokens) and tokens[pos[0]][0] == 'OP' and tokens[pos[0]][1] in ('+', '-'):
            op = tokens[pos[0]][1]
            pos[0] += 1
            right = parse_term()
            if op == '+':
                left = left + right
            else:
                left = left - right
        return left
    
    def parse_term():
        """Parse multiplication (higher precedence)"""
        left = parse_factor()
        while pos[0] < len(tokens) and tokens[pos[0]][0] == 'OP' and tokens[pos[0]][1] == '*':
            pos[0] += 1
            right = parse_factor()
            left = left * right
        return left
    
    def parse_factor():
        """Parse numbers and parenthesized expressions"""
        if pos[0] < len(tokens):
            if tokens[pos[0]][0] == 'NUM':
                num = tokens[pos[0]][1]
                pos[0] += 1
                return num
            elif tokens[pos[0]][0] == 'OP' and tokens[pos[0]][1] == '(':
                pos[0] += 1  # consume '('
                result = parse_expr()
                if pos[0] < len(tokens) and tokens[pos[0]][0] == 'OP' and tokens[pos[0]][1] == ')':
                    pos[0] += 1  # consume ')'
                else:
                    raise ValueError("Missing closing parenthesis")
                return result
            else:
                raise ValueError(f"Unexpected token: {tokens[pos[0]]}")
        else:
            raise ValueError("Unexpected end of expression")
    
    result = parse_expr()
    if pos[0] != len(tokens):
        raise ValueError(f"Unexpected tokens after expression: {tokens[pos[0]:]}")
    return result

# Read input
expr = sys.stdin.read().strip()
if not expr:
    raise ValueError("Empty expression")

result = evaluate(expr)
print(result)
EOF

echo "DONE" > answer.txt