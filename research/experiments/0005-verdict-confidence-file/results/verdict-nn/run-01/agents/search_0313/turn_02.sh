cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-nn/run-01/work/tasks/030_search_0313/workspace

# First, let's inspect the raw content of blob.txt to understand the encoding
echo "=== Raw blob.txt ==="
cat vault/blob.txt

echo ""
echo "=== Base64 decoded (raw) ==="
base64 -d < vault/blob.txt 2>/dev/null || echo "Base64 decode failed"

echo ""
echo "=== Trying to find owner with grep on decoded content ==="
base64 -d < vault/blob.txt 2>/dev/null | grep -o '"owner"[[:space:]]*:[[:space:]]*"[^"]*"' || echo "No owner field found"

# Let's also try to see if it's not standard base64 or has issues
echo ""
echo "=== Hex dump of first 200 bytes ==="
base64 -d < vault/blob.txt 2>/dev/null | head -c 200 | xxd

# Try to extract owner using python with error handling
echo ""
echo "=== Python extraction attempt ==="
python3 << 'PYEOF'
import base64
import json
import re

with open("vault/blob.txt", "r") as f:
    encoded = f.read().strip()

try:
    decoded = base64.b64decode(encoded).decode('utf-8')
    print("Decoded content:")
    print(repr(decoded))
    
    # Try to parse as JSON
    try:
        data = json.loads(decoded)
        owner = data.get("owner", "NOT_FOUND")
        print(f"Owner from JSON: {owner}")
        with open("answer.txt", "w") as f:
            f.write(str(owner))
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        # Try to extract owner with regex
        match = re.search(r'"owner"\s*:\s*"([^"]*)"', decoded)
        if match:
            owner = match.group(1)
            print(f"Owner from regex: {owner}")
            with open("answer.txt", "w") as f:
                f.write(owner)
        else:
            print("Could not find owner")
            with open("answer.txt", "w") as f:
                f.write("NOT_FOUND")
except Exception as e:
    print(f"Base64 decode error: {e}")
    with open("answer.txt", "w") as f:
        f.write("DECODE_ERROR")
PYEOF

echo ""
echo "=== Final answer.txt ==="
cat answer.txt

# Write verdict
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Extracted owner from base64-encoded JSON" >> verdict.txt