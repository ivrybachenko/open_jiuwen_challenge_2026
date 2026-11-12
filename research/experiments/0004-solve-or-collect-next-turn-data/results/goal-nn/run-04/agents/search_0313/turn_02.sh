cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-04/work/tasks/030_search_0313/workspace

# First, let's see what the raw blob.txt looks like and try decoding it
echo "=== Raw blob.txt ==="
cat vault/blob.txt

echo ""
echo "=== Base64 decoded (raw) ==="
base64 -d < vault/blob.txt 2>/dev/null || echo "Base64 decode failed"

echo ""
echo "=== Trying with python to handle potential padding issues ==="
python3 -c "
import base64, json, sys

with open('vault/blob.txt', 'r') as f:
    encoded = f.read().strip()

# Try standard base64 decode
try:
    decoded = base64.b64decode(encoded)
    print('Decoded bytes:', decoded)
    text = decoded.decode('utf-8')
    print('Decoded text:', text)
    try:
        data = json.loads(text)
        print('JSON owner:', data.get('owner', 'NOT_FOUND'))
    except json.JSONDecodeError as e:
        print('JSON error:', e)
        # Try to find owner with regex as fallback
        import re
        match = re.search(r'\"owner\"\\s*:\\s*\"([^\"]+)\"', text)
        if match:
            print('Regex owner:', match.group(1))
        else:
            print('Owner not found in JSON-like text')
except Exception as e:
    print('Decode error:', e)
" > answer.txt 2>&1

echo "=== answer.txt content ==="
cat answer.txt