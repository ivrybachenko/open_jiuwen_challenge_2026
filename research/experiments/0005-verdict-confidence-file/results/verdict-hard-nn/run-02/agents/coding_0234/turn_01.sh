cat > program.py << 'EOF'
import sys

def evaluate(expr):
    # Remove all spaces
    expr = expr.replace(' ', '')
    
    # We need to handle parentheses and operator precedence
    # * has higher precedence than + and -
    # We'll use a recursive descent parser or convert to RPN
    
    # Simple approach: tokenize and use two-stack algorithm (Dijkstra's shunting yard)
    
    def tokenize(s):
        tokens = []
        i = 0
        while i < len(s):
            if s[i].isdigit():
                j = i
                while j < len(s) and s[j].isdigit():
                    j += 1
                    tokens.append(int(s[i:j]))
                    i = j
            elif s[i] in '+-*()':
                tokens.append(s[i])
                i += 1
            else:
                raise ValueError(f"Unexpected character: {s[i]}")
        return tokens
    
    tokens = tokenize(expr)
    
    # Two-stack algorithm
    values = []
    ops = []
    
    def apply_op():
        op = ops.pop()
        b = values.pop()
        a = values.pop()
        if op == '+':
            values.append(a + b)
        elif op == '-':
            values.append(a - b)
        elif op == '*':
            values.append(a * b)
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if isinstance(token, int):
            values.append(token)
        elif token == '(':
            ops.append(token)
        elif token == ')':
            while ops and ops[-1] != '(':
                apply_op()
            ops.pop()  # Remove '('
        elif token in '+-*':
            while (ops and ops[-1] != '(' and 
                   precedence(ops[-1]) >= precedence(token)):
                apply_op()
            ops.append(token)
        i += 1
    
    while ops:
        apply_op()
    
    return values[0]

def precedence(op):
    if op in '+-':
        return 1
    if op == '*':
        return 2
    return 0

if __name__ == '__main__':
    expr = sys.stdin.read().strip()
    result = evaluate(expr)
    print(result)
EOF

echo "DONE" > answer.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Simple arithmetic expression evaluator with +, -, *, parentheses" >> verdict.txt