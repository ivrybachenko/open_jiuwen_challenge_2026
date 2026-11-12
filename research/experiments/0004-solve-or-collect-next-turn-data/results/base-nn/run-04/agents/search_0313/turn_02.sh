# First, let's inspect the raw content of blob.txt to understand the encoding
echo "=== Raw blob.txt ==="
cat vault/blob.txt
echo ""
echo "=== Base64 decode attempt 1 (standard) ==="
base64 -d vault/blob.txt 2>/dev/null | head -c 500
echo ""
echo "=== Base64 decode attempt 2 (ignore garbage) ==="
base64 -d vault/blob.txt 2>/dev/null | python3 -c "
import sys, json
data = sys.stdin.read()
# Try to find JSON-like content
try:
    obj = json.loads(data)
    print('owner:', obj.get('owner', 'NOT_FOUND'))
except:
    # Try to extract JSON from the decoded content
    import re
    match = re.search(r'\{.*\}', data, re.DOTALL)
    if match:
        try:
            obj = json.loads(match.group())
            print('owner:', obj.get('owner', 'NOT_FOUND'))
        except:
            print('Could not parse JSON from:', repr(data[:200]))
    else:
        print('No JSON found in decoded content:', repr(data[:200]))
"
echo ""
echo "=== Check if file might be double-encoded or has issues ==="
xxd vault/blob.txt | head -20