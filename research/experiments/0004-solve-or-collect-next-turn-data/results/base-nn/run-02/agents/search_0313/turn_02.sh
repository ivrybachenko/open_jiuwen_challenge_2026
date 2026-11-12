cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/base-nn/run-02/work/tasks/030_search_0313/workspace

# First, let's inspect the raw content of blob.txt to understand the encoding
echo "=== Raw blob.txt ==="
cat vault/blob.txt

echo ""
echo "=== Decoded content ==="
base64 -d vault/blob.txt 2>/dev/null || echo "base64 decode failed, trying with padding fix"

echo ""
echo "=== Trying with padding fix ==="
# base64 might need padding
python3 -c "
import base64, json, sys

with open('vault/blob.txt', 'r') as f:
    encoded = f.read().strip()

# Try to decode with padding
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
        # Try to find owner field manually
        import re
        match = re.search(r'\"owner\"\\s*:\\s*\"([^\"]+)\"', text)
        if match:
            print('Manual owner:', match.group(1))
        else:
            print('Owner not found in text')
except Exception as e:
    print('Decode error:', e)
" > answer.txt 2>&1

cat answer.txt