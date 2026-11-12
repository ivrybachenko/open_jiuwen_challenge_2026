cat > program.py << 'EOF'
import sys

def parse_expression(s):
    """Parse and evaluate an arithmetic expression with +, -, * and parentheses."""
    s = s.strip()
    if not s:
        raise ValueError("Empty expression")
    
    # We'll use a recursive descent parser
    # Grammar:
    # expression = term (('+' | '-') term)*
    # term = factor (('*' | '/') factor)*
    # factor = NUMBER | '(' expression ')'
    
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
    
    def parse_number():
        skip_spaces()
        start = pos[0]
        while pos[0] < len(s) and s[pos[0]].isdigit():
            pos[0] += 1
        if pos[0] == start:
            raise ValueError(f"Expected number at position {pos[0]}")
        return int(s[start:pos[0]])
    
    def parse_factor():
        skip_spaces()
        ch = peek()
        if ch is None:
            raise ValueError("Unexpected end of expression")
        if ch == '(':
            consume()  # consume '('
            result = parse_expression()
            skip_spaces()
            if peek() != ')':
                raise ValueError("Expected ')'")
            consume()  # consume ')'
            return result
        elif ch.isdigit():
            return parse_number()
        else:
            raise ValueError(f"Unexpected character: {ch}")
    
    def parse_term():
        left = parse_factor()
        while True:
            skip_spaces()
            ch = peek()
            if ch == '*':
                consume()
                right = parse_factor()
                left = left * right
            elif ch == '/':
                consume()
                right = parse_factor()
                if right == 0:
                    raise ValueError("Division by zero")
                left = left // right
            else:
                break
        return left
    
    def parse_expression():
        left = parse_term()
        while True:
            skip_spaces()
            ch = peek()
            if ch == '+':
                consume()
                right = parse_term()
                left = left + right
            elif ch == '-':
                consume()
                right = parse_term()
                left = left - right
            else:
                break
        return left
    
    result = parse_expression()
    skip_spaces()
    if pos[0] != len(s):
        raise ValueError(f"Unexpected characters after expression at position {pos[0]}")
    return result

if __name__ == "__main__":
    expr = sys.stdin.read().strip()
    if not expr:
        raise ValueError("No input provided")
    result = parse_expression(expr)
    print(result)
EOF

echo "DONE" > answer.txt