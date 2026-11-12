cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/base-nn/run-03/work/tasks/030_search_0313/workspace

# First, let's inspect the raw content of blob.txt to understand the encoding
echo "=== Raw blob.txt ==="
cat vault/blob.txt

echo ""
echo "=== Hex dump of first 100 bytes ==="
xxd vault/blob.txt | head -20

echo ""
echo "=== Try base64 decode ==="
base64 -d vault/blob.txt 2>/dev/null | head -c 500
echo ""

echo ""
echo "=== Try base64 -d with padding fix ==="
# Sometimes base64 needs padding
base64 -d vault/blob.txt 2>/dev/null > /tmp/decoded.json || true
cat /tmp/decoded.json | head -c 500
echo ""

echo ""
echo "=== Check if it's already JSON or needs different decoding ==="
# Try to see if the file content itself is the JSON (maybe not base64 encoded?)
python3 -c "
import base64, json, sys

with open('vault/blob.txt', 'r') as f:
    content = f.read().strip()

# Try direct JSON parse
try:
    data = json.loads(content)
    print('Direct JSON parse succeeded')
    print('Owner:', data.get('owner', 'NOT_FOUND'))
    sys.exit(0)
except:
    pass

# Try base64 decode
try:
    decoded = base64.b64decode(content)
    data = json.loads(decoded)
    print('Base64 decode + JSON parse succeeded')
    print('Owner:', data.get('owner', 'NOT_FOUND'))
    sys.exit(0)
except Exception as e:
    print(f'Base64 decode failed: {e}')

# Try base64 with padding
try:
    import base64
    # Add padding if needed
    missing_padding = len(content) % 4
    if missing_padding:
        content_padded = content + '=' * (4 - missing_padding)
    else:
        content_padded = content
    decoded = base64.b64decode(content_padded)
    data = json.loads(decoded)
    print('Base64 with padding succeeded')
    print('Owner:', data.get('owner', 'NOT_FOUND'))
    sys.exit(0)
except Exception as e:
    print(f'Base64 with padding failed: {e}')

# Try URL-safe base64
try:
    decoded = base64.urlsafe_b64decode(content + '==')
    data = json.loads(decoded)
    print('URL-safe base64 succeeded')
    print('Owner:', data.get('owner', 'NOT_FOUND'))
    sys.exit(0)
except Exception as e:
    print(f'URL-safe base64 failed: {e}')

print('ALL METHODS FAILED')
" > answer.txt 2>&1

cat answer.txt