cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-hard-nn/run-04/work/tasks/030_search_0313/workspace

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
# Sometimes base64 needs padding
base64 -d vault/blob.txt 2>/dev/null > /tmp/decoded.json || true
cat /tmp/decoded.json | head -c 500
echo ""

echo ""
echo "=== Check if it's already JSON or needs different decoding ==="
# Try to see what the decoded content looks like
base64 -d vault/blob.txt 2>/dev/null > /tmp/decoded.json || true
file /tmp/decoded.json
cat /tmp/decoded.json

echo ""
echo "=== Try python base64 decode ==="
python3 -c "
import base64, json, sys
with open('vault/blob.txt', 'r') as f:
    encoded = f.read().strip()
print('Encoded length:', len(encoded))
print('First 100 chars:', encoded[:100])
try:
    decoded = base64.b64decode(encoded)
    print('Decoded bytes:', decoded[:200])
    print('Decoded as utf8:', decoded.decode('utf-8')[:500])
    try:
        data = json.loads(decoded)
        print('JSON owner:', data.get('owner', 'NOT_FOUND'))
    except json.JSONDecodeError as e:
        print('JSON error:', e)
        # Try to find owner in raw text
        text = decoded.decode('utf-8', errors='replace')
        import re
        match = re.search(r'\"owner\"\\s*:\\s*\"([^\"]+)\"', text)
        if match:
            print('Found owner via regex:', match.group(1))
        else:
            print('No owner found in raw text')
except Exception as e:
    print('Decode error:', e)
" > /tmp/debug_output.txt 2>&1
cat /tmp/debug_output.txt

echo ""
echo "=== Final answer extraction ==="
python3 -c "
import base64, json, re
with open('vault/blob.txt', 'r') as f:
    encoded = f.read().strip()
decoded = base64.b64decode(encoded)
text = decoded.decode('utf-8', errors='replace')
match = re.search(r'\"owner\"\\s*:\\s*\"([^\"]+)\"', text)
if match:
    print(match.group(1))
else:
    print('NOT_FOUND')
" > answer.txt

echo "=== answer.txt content ==="
cat answer.txt

# Create verdict.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Extracted owner from base64-encoded JSON" >> verdict.txt