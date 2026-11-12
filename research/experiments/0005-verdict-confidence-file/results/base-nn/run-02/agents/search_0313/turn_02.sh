cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/base-nn/run-02/work/tasks/030_search_0313/workspace

# First, let's see what the raw content looks like
echo "=== Raw blob.txt ==="
cat vault/blob.txt

echo ""
echo "=== Base64 decoded (raw) ==="
base64 -d < vault/blob.txt 2>/dev/null || echo "Base64 decode failed"

echo ""
echo "=== Try with python base64 ==="
python3 -c "
import base64, json, sys

with open('vault/blob.txt', 'r') as f:
    encoded = f.read().strip()

try:
    decoded = base64.b64decode(encoded)
    print('Decoded bytes:', decoded)
    print('Decoded string:', decoded.decode('utf-8'))
    data = json.loads(decoded)
    print('JSON data:', data)
    print('Owner:', data.get('owner', 'NOT_FOUND'))
except Exception as e:
    print('Error:', e)
    # Try to find owner with regex as fallback
    import re
    text = decoded.decode('utf-8', errors='replace')
    match = re.search(r'\"owner\"\\s*:\\s*\"([^\"]+)\"', text)
    if match:
        print('Owner (regex):', match.group(1))
    else:
        print('Owner not found')
" > answer.txt 2>&1

cat answer.txt