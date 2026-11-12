cat > /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-04/work/tasks/002_coding_0210/workspace/brackets.py << 'PYEOF'
def balanced(text):
    stack = []
    matching = {')': '(', ']': '[', '}': '{'}
    for ch in text:
        if ch in '([{':
            stack.append(ch)
        elif ch in ')]}':
            if not stack or stack[-1] != matching[ch]:
                return False
            stack.pop()
    return len(stack) == 0
PYEOF

cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-04/work/tasks/002_coding_0210/workspace
python3 test_brackets.py
echo "DONE" > answer.txt