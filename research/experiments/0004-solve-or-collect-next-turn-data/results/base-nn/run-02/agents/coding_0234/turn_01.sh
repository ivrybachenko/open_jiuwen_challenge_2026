cat > program.py << 'EOF'
import sys

def parse_expression(s):
    """Parse and evaluate an arithmetic expression with +, -, * and parentheses."""
    s = s.strip()
    if not s:
        return 0
    
    # We'll use a recursive descent parser
    # Grammar:
    # expression = term (('+' | '-') term)*
    # term = factor (('*' | '/' | '%') factor)*  -- but only * is allowed per spec
    # factor = NUMBER | '(' expression ')'
    
    pos = [0]  # Use list to allow mutation in nested functions
    
    def peek():
        if pos[0] < len(s):
            return s[pos[0]]
        return None
    
    def consume(expected=None):
        if expected is not None:
            if pos[0] >= len(s) or s[pos[0]] != expected:
                raise ValueError(f"Expected '{expected}' at position {pos[0]}")
        pos[0] += 1
    
    def parse_number():
        start = pos[0]
        while pos[0] < len(s) and s[pos[0]].isdigit():
            pos[0] += 1
        if start == pos[0]:
            raise ValueError(f"Expected number at position {pos[0]}")
        return int(s[start:pos[0]])
    
    def parse_factor():
        token = peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        if token == '(':
            consume()  # consume '('
            result = parse_expression()
            if peek() != ')':
                raise ValueError("Expected ')'")
            consume()  # consume ')'
            return result
        elif token.isdigit():
            return parse_number()
        else:
            raise ValueError(f"Unexpected character '{token}' at position {pos[0]}")
    
    def parse_term():
        left = parse_factor()
        while peek() in ('*',):
            op = consume()  # consume '*'
            right = parse_factor()
            if op == '*':
                left = left * right
        return left
    
    def parse_expression():
        left = parse_term()
        while peek() in ('+', '-'):
            op = consume()  # consume '+' or '-'
            right = parse_term()
            if op == '+':
                left = left + right
            elif op == '-':
                left = left - right
        return left
    
    result = parse_expression()
    return result

if __name__ == '__main__':
    expr = sys.stdin.read().strip()
    if not expr:
        print(0)
    else:
        print(parse_expression(expr))
EOF

echo "DONE" > answer.txt