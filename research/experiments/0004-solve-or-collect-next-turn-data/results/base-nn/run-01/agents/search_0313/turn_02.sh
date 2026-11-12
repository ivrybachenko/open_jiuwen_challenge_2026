cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/base-nn/run-01/work/tasks/030_search_0313/workspace

# First, let's see what's in the blob file
echo "=== Raw blob content ==="
cat vault/blob.txt

echo ""
echo "=== Base64 decoded content ==="
base64 -d vault/blob.txt 2>/dev/null || echo "Base64 decode failed, trying with padding fix"

echo ""
echo "=== Trying with padding fix ==="
# Base64 might need padding
python3 -c "
import base64, json, sys

with open('vault/blob.txt', 'r') as f:
    encoded = f.read().strip()

# Try to decode with padding fix
try:
    # Add padding if needed
    missing_padding = len(encoded) % 4
    if missing_padding:
        encoded += '=' * (4 - missing_padding)
    decoded = base64.b64decode(encoded)
    print('Decoded bytes:', decoded)
    print('Decoded string:', decoded.decode('utf-8', errors='replace'))
    
    # Try to parse as JSON
    try:
        data = json.loads(decoded)
        print('JSON owner:', data.get('owner', 'NOT FOUND'))
    except json.JSONDecodeError as e:
        print('JSON parse error:', e)
        # Try to find 'owner' in the raw decoded text
        text = decoded.decode('utf-8', errors='replace')
        import re
        match = re.search(r'\"owner\"\\s*:\\s*\"([^\"]+)\"', text)
        if match:
            print('Found owner via regex:', match.group(1))
        else:
            print('Owner not found in decoded content')
except Exception as e:
    print('Decode error:', e)
" > answer.txt 2>&1

cat answer.txt