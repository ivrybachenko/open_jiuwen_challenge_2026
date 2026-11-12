cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-01/work/tasks/030_search_0313/workspace

# First, let's see what the raw blob.txt looks like and try decoding it
echo "=== Raw blob.txt ==="
cat vault/blob.txt

echo ""
echo "=== Decoded content ==="
base64 -d < vault/blob.txt 2>/dev/null || echo "base64 decode failed"

echo ""
echo "=== Trying with python ==="
python3 -c "
import base64, json, sys

with open('vault/blob.txt', 'r') as f:
    encoded = f.read().strip()

try:
    decoded = base64.b64decode(encoded).decode('utf-8')
    print('Decoded:', repr(decoded))
    try:
        data = json.loads(decoded)
        print('JSON parsed successfully')
        print('Owner:', data.get('owner', 'NOT_FOUND'))
    except json.JSONDecodeError as e:
        print('JSON parse error:', e)
        # Try to find owner field manually
        import re
        match = re.search(r'\"owner\"\\s*:\\s*\"([^\"]+)\"', decoded)
        if match:
            print('Owner (regex):', match.group(1))
        else:
            print('Owner not found via regex')
except Exception as e:
    print('Decode error:', e)
" > answer.txt 2>&1

cat answer.txt