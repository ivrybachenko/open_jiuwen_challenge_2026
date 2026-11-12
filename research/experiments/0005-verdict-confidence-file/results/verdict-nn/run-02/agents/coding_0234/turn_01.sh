cat > program.py << 'EOF'
import sys

def evaluate(expr):
    # Remove all spaces
    expr = expr.replace(' ', '')
    
    # We'll use a recursive descent parser
    # Grammar:
    # expression = term (('+' | '-') term)*
    # term = factor (('*' | '/' | '%') factor)*
    # factor = NUMBER | '(' expression ')'
    
    pos = [0]  # Use list to allow mutation in nested functions
    
    def peek():
        if pos[0] < len(expr):
            return expr[pos[0]]
        return None
    
    def consume():
        ch = expr[pos[0]]
        pos[0] += 1
        return ch
    
    def parse_number():
        start = pos[0]
        while pos[0] < len(expr) and expr[pos[0]].isdigit():
            pos[0] += 1
        return int(expr[start:pos[0]])
    
    def parse_factor():
        ch = peek()
        if ch == '(':
            consume()  # consume '('
            result = parse_expression()
            if peek() == ')':
                consume()  # consume ')'
            else:
                raise ValueError("Missing closing parenthesis")
            return result
        elif ch.isdigit():
            return parse_number()
        else:
            raise ValueError(f"Unexpected character: {ch}")
    
    def parse_term():
        result = parse_factor()
        while peek() in ('*', '/', '%'):
            op = consume()
            right = parse_factor()
            if op == '*':
                result *= right
            elif op == '/':
                result //= right
            elif op == '%':
                result %= right
        return result
    
    def parse_expression():
        result = parse_term()
        while peek() in ('+', '-'):
            op = consume()
            right = parse_term()
            if op == '+':
                result += right
            elif op == '-':
                result -= right
        return result
    
    return parse_expression()

if __name__ == '__main__':
    expr = sys.stdin.read().strip()
    if not expr:
        print(0)
    else:
        print(evaluate(expr))
EOF

echo "DONE" > answer.txt