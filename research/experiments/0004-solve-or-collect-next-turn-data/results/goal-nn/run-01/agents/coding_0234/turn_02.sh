cat > program.py << 'PYEOF'
import sys

def main():
    expression = sys.stdin.read().strip()
    if not expression:
        return
    result = eval(expression)
    print(result)

if __name__ == "__main__":
    main()
PYEOF

echo "DONE" > answer.txt