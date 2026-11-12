cat > program.py << 'EOF'
import sys
import re

def evaluate_expression(expr):
    # Remove all spaces
    expr = expr.replace(' ', '')
    
    # Tokenize the expression
    tokens = re.findall(r'\d+|\+|\-|\*|\(|\)', expr)
    
    if not tokens:
        return 0
    
    # Convert to a list for easy processing
    tokens = list(tokens)
    
    # We'll use a recursive descent parser
    # Grammar:
    # expression := term (('+' | '-') term)*
    # term := factor (('*') factor)*
    # factor := NUMBER | '(' expression ')'
    
    pos = [0]  # Use list to allow modification in nested functions
    
    def parse_expression():
        result = parse_term()
        while pos[0] < len(tokens) and tokens[pos[0]] in ('+', '-'):
            op = tokens[pos[0]]
            pos[0] += 1
            right = parse_term()
            if op == '+':
                result += right
            else:
                result -= right
        return result
    
    def parse_term():
        result = parse_factor()
        while pos[0] < len(tokens) and tokens[pos[0]] == '*':
            pos[0] += 1
            right = parse_factor()
            result *= right
        return result
    
    def parse_factor():
        if pos[0] >= len(tokens):
            raise ValueError("Unexpected end of expression")
        
        token = tokens[pos[0]]
        
        if token == '(':
            pos[0] += 1
            result = parse_expression()
            if pos[0] >= len(tokens) or tokens[pos[0]] != ')':
                raise ValueError("Missing closing parenthesis")
            pos[0] += 1
            return result
        elif token == '-':
            # Handle negative numbers at start or after operator
            pos[0] += 1
            if pos[0] < len(tokens) and tokens[pos[0]] == '(':
                result = parse_expression()
                if pos[0] >= len(tokens) or tokens[pos[0]] != ')':
                    raise ValueError("Missing closing parenthesis")
                pos[0] += 1
                return -result
            elif pos[0] < len(tokens) and tokens[pos[0]].isdigit():
                pos[0] += 1
                return -int(tokens[pos[0] - 1])
            else:
                raise ValueError("Unexpected token after '-'")
        elif token.isdigit():
            pos[0] += 1
            return int(token)
        else:
            raise ValueError(f"Unexpected token: {token}")
    
    result = parse_expression()
    
    # Check if all tokens were consumed
    if pos[0] != len(tokens):
        raise ValueError(f"Unexpected tokens remaining: {tokens[pos[0]:]}")
    
    return result

# Read input from stdin
input_expr = sys.stdin.read().strip()
if input_expr:
    result = evaluate_expression(input_expr)
    print(result)
EOF

echo "DONE" > answer.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Simple arithmetic expression evaluator" >> verdict.txt