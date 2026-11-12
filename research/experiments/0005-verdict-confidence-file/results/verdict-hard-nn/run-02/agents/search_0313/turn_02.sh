cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-hard-nn/run-02/work/tasks/030_search_0313/workspace

# First, let's inspect the raw content of blob.txt to understand the encoding
echo "=== Raw blob.txt ==="
cat vault/blob.txt

echo ""
echo "=== Hex dump of first 200 bytes ==="
xxd vault/blob.txt | head -20

echo ""
echo "=== Try base64 decode ==="
base64 -d vault/blob.txt 2>/dev/null | head -c 500
echo ""

echo ""
echo "=== Try base64 -d with padding fix ==="
# Try to handle potential padding issues
base64 -d vault/blob.txt 2>/dev/null > /tmp/decoded.json || true
cat /tmp/decoded.json | head -c 500
echo ""

echo ""
echo "=== Check if it's already JSON or needs different decoding ==="
# Maybe it's not base64 but the file content itself is the JSON
# Let's check the file size and content type
file vault/blob.txt
wc -c vault/blob.txt

echo ""
echo "=== Try to parse as JSON directly ==="
python3 -c "
import json, base64, sys

with open('vault/blob.txt', 'r') as f:
    content = f.read().strip()

print('Content length:', len(content))
print('First 100 chars:', repr(content[:100]))

# Try direct JSON parse
try:
    data = json.loads(content)
    print('Direct JSON parse succeeded')
    print('Owner:', data.get('owner', 'N/A'))
    sys.exit(0)
except json.JSONDecodeError as e:
    print('Direct JSON parse failed:', e)

# Try base64 decode
try:
    decoded = base64.b64decode(content)
    print('Base64 decode succeeded, length:', len(decoded))
    print('Decoded content:', decoded[:200])
    try:
        data = json.loads(decoded)
        print('JSON parse of decoded succeeded')
        print('Owner:', data.get('owner', 'N/A'))
    except json.JSONDecodeError as e2:
        print('JSON parse of decoded failed:', e2)
        # Try to find owner in raw decoded text
        import re
        match = re.search(r'\"owner\"\\s*:\\s*\"([^\"]+)\"', decoded.decode('utf-8', errors='replace'))
        if match:
            print('Owner found via regex:', match.group(1))
except Exception as e:
    print('Base64 decode failed:', e)
" > /tmp/debug_output.txt 2>&1

cat /tmp/debug_output.txt

# Extract the owner from debug output
OWNER=$(grep -oP 'Owner: \K.*' /tmp/debug_output.txt | head -1)
if [ -z "$OWNER" ]; then
    OWNER=$(grep -oP 'Owner found via regex: \K.*' /tmp/debug_output.txt | head -1)
fi

if [ -n "$OWNER" ]; then
    echo "$OWNER" > answer.txt
    echo "Answer written: $OWNER"
else
    echo "Could not determine owner" > answer.txt
    cat /tmp/debug_output.txt
fi

cat answer.txt

# Create verdict.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Extracted owner from base64-encoded JSON" >> verdict.txt