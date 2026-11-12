cat > program.py << 'PYEOF'
import sys
import ast
import operator

def safe_eval(node):
    if isinstance(node, ast.Expression):
        return safe_eval(node.body)
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, int):
            return node.value
        else:
            raise ValueError(f"Unsupported constant: {node.value}")
    elif isinstance(node, ast.Num):
        if isinstance(node.n, int):
            return node.n
        else:
            raise ValueError(f"Unsupported number: {node.n}")
    elif isinstance(node, ast.BinOp):
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        elif isinstance(node.op, ast.Mult):
            return left * right
        else:
            raise ValueError(f"Unsupported operator: {type(node.op)}")
    else:
        raise ValueError(f"Unsupported node type: {type(node)}")

def evaluate_expression(expression):
    try:
        tree = ast.parse(expression, mode='eval')
        result = safe_eval(tree)
        return result
    except Exception as e:
        raise ValueError(f"Failed to evaluate expression: {expression}. Error: {e}")

def main():
    expression = sys.stdin.read().strip()
    if not expression:
        print(0)
        return
    result = evaluate_expression(expression)
    print(result)

if __name__ == "__main__":
    main()
PYEOF

echo "DONE" > answer.txt