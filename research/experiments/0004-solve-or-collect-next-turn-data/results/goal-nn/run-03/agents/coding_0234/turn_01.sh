cat > program.py << 'EOF'
import sys

def evaluate(expr):
    # Remove all spaces
    expr = expr.replace(' ', '')
    
    # We need to handle parentheses and operator precedence
    # * has higher precedence than + and -
    # We'll use a recursive descent parser or convert to a form we can evaluate
    
    # Simple approach: tokenize and use two-stack algorithm (Shunting-yard or direct evaluation)
    
    def tokenize(s):
        tokens = []
        i = 0
        while i < len(s):
            if s[i].isdigit():
                j = i
                while j < len(s) and s[j].isdigit():
                    j += 1
                tokens.append(('NUM', int(s[i:j])))
                i = j
            elif s[i] in '+-*()':
                tokens.append(('OP', s[i]))
                i += 1
            else:
                raise ValueError(f"Unexpected character: {s[i]}")
        return tokens
    
    tokens = tokenize(expr)
    
    # Recursive descent parser
    # Grammar:
    # expr -> term (('+' | '-') term)*
    # term -> factor (('*') factor)*
    # factor -> NUM | '(' expr ')'
    
    pos = [0]  # Use list to allow mutation in nested functions
    
    def parse_expr():
        result = parse_term()
        while pos[0] < len(tokens) and tokens[pos[0]][0] == 'OP' and tokens[pos[0]][1] in ('+', '-'):
            op = tokens[pos[0]][1]
            pos[0] += 1
            right = parse_term()
            if op == '+':
                result += right
            else:
                result -= right
        return result
    
    def parse_term():
        result = parse_factor()
        while pos[0] < len(tokens) and tokens[pos[0]][0] == 'OP' and tokens[pos[0]][1] == '*':
            pos[0] += 1
            right = parse_factor()
            result *= right
        return result
    
    def parse_factor():
        if pos[0] >= len(tokens):
            raise ValueError("Unexpected end of expression")
        
        token = tokens[pos[0]]
        
        if token[0] == 'NUM':
            pos[0] += 1
            return token[1]
        elif token[0] == 'OP' and token[1] == '(':
            pos[0] += 1
            result = parse_expr()
            if pos[0] >= len(tokens) or tokens[pos[0]][1] != ')':
                raise ValueError("Missing closing parenthesis")
            pos[0] += 1
            return result
        else:
            raise ValueError(f"Unexpected token: {token}")
    
    result = parse_expr()
    
    # Check that all tokens were consumed
    if pos[0] < len(tokens):
        raise ValueError(f"Unexpected tokens after expression: {tokens[pos[0]:]}")
    
    return result

if __name__ == '__main__':
    expr = sys.stdin.read().strip()
    if not expr:
        raise ValueError("Empty expression")
    result = evaluate(expr)
    print(result)
EOF

echo "DONE" > answer.txt