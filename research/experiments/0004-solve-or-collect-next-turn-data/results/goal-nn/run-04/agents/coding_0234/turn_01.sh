cat > program.py << 'EOF'
import sys

def evaluate(expr):
    # Remove all spaces
    expr = expr.replace(' ', '')
    
    # We need to handle parentheses and operator precedence
    # * has higher precedence than + and -
    # We'll use a recursive descent parser or convert to a form we can evaluate
    
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
    
    # Shunting yard to convert to postfix, then evaluate
    # Operators: +, - have same precedence, left-associative
    # *: higher precedence, left-associative
    
    output_queue = []
    operator_stack = []
    
    precedence = {'+': 1, '-': 1, '*': 2}
    
    for token in tokens:
        if isinstance(token, int):
            output_queue.append(token)
        elif token in precedence:
            while (operator_stack and 
                   operator_stack[-1] != '(' and
                   operator_stack[-1] in precedence and
                   precedence[operator_stack[-1]] >= precedence[token]):
                output_queue.append(operator_stack.pop())
            operator_stack.append(token)
        elif token == '(':
            operator_stack.append(token)
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                output_queue.append(operator_stack.pop())
            if operator_stack and operator_stack[-1] == '(':
                operator_stack.pop()  # Remove '('
            else:
                raise ValueError("Mismatched parentheses")
    
    while operator_stack:
        op = operator_stack.pop()
        if op == '(':
            raise ValueError("Mismatched parentheses")
        output_queue.append(op)
    
    # Evaluate postfix expression
    stack = []
    for token in output_queue:
        if isinstance(token, int):
            stack.append(token)
        else:
            if len(stack) < 2:
                raise ValueError("Invalid expression")
            b = stack.pop()
            a = stack.pop()
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
    
    if len(stack) != 1:
        raise ValueError("Invalid expression")
    
    return stack[0]

# Read input
expr = sys.stdin.read().strip()
if not expr:
    raise ValueError("Empty expression")

result = evaluate(expr)
print(result)
EOF

echo "DONE" > answer.txt