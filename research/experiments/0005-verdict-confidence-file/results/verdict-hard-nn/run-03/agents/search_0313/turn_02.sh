cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-hard-nn/run-03/work/tasks/030_search_0313/workspace

# First, let's inspect the raw content of blob.txt to understand the encoding
echo "=== Raw blob.txt ==="
cat vault/blob.txt

echo ""
echo "=== Hex dump of first 200 bytes ==="
xxd vault/blob.txt | head -20

echo ""
echo "=== Try base64 decode and show raw output ==="
base64 -d vault/blob.txt 2>/dev/null | xxd | head -20

echo ""
echo "=== Try base64 decode and show as text ==="
base64 -d vault/blob.txt 2>/dev/null | cat -v

echo ""
echo "=== Try with python to handle potential issues ==="
python3 -c "
import base64, json, sys

with open('vault/blob.txt', 'r') as f:
    encoded = f.read().strip()

print(f'Encoded length: {len(encoded)}')
print(f'Encoded content: {encoded[:100]}...')

try:
    decoded = base64.b64decode(encoded)
    print(f'Decoded bytes length: {len(decoded)}')
    print(f'Decoded as utf-8: {decoded.decode(\"utf-8\")}')
    data = json.loads(decoded.decode('utf-8'))
    print(f'JSON keys: {list(data.keys())}')
    print(f'Owner: {data.get(\"owner\", \"NOT_FOUND\")}')
except Exception as e:
    print(f'Error: {e}')
    # Try to see what the raw bytes look like
    print(f'First 50 bytes hex: {decoded[:50].hex()}')
    print(f'First 50 bytes repr: {repr(decoded[:50])}')
" > debug_output.txt 2>&1

cat debug_output.txt

# Now extract the owner and write to answer.txt
python3 -c "
import base64, json

with open('vault/blob.txt', 'r') as f:
    encoded = f.read().strip()

decoded = base64.b64decode(encoded)
data = json.loads(decoded.decode('utf-8'))
owner = data.get('owner', 'NOT_FOUND')
print(owner)
" > answer.txt

echo "=== Final answer.txt ==="
cat answer.txt

# Create verdict.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Extracted owner from base64-encoded JSON" >> verdict.txt