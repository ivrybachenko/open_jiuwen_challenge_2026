cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-02/work/tasks/030_search_0313/workspace

# First, let's see what's in the blob file and try to decode it
echo "=== Raw blob content ==="
cat vault/blob.txt

echo ""
echo "=== Base64 decoded (raw) ==="
base64 -d < vault/blob.txt 2>/dev/null || echo "Base64 decode failed"

echo ""
echo "=== Trying to find owner with grep ==="
# Try base64 decode and grep for owner
base64 -d < vault/blob.txt 2>/dev/null | grep -i owner || echo "No owner found via grep"

echo ""
echo "=== Trying python with the harness venv ==="
/Users/zbr174/dev/open_jiuwen_challenge_2026/harness/.venv/bin/python3 -c "
import base64, json, sys

with open('vault/blob.txt', 'r') as f:
    encoded = f.read().strip()

# Try standard base64 decode
try:
    decoded = base64.b64decode(encoded).decode('utf-8')
    print('Decoded JSON:', repr(decoded))
    data = json.loads(decoded)
    print('Owner:', data.get('owner', 'NOT_FOUND'))
except Exception as e:
    print('Standard decode failed:', e)
    
    # Try URL-safe base64
    try:
        decoded = base64.urlsafe_b64decode(encoded).decode('utf-8')
        print('URL-safe decoded:', repr(decoded))
        data = json.loads(decoded)
        print('Owner:', data.get('owner', 'NOT_FOUND'))
    except Exception as e2:
        print('URL-safe decode failed:', e2)
        
        # Try with padding
        import base64
        padded = encoded + '=' * (4 - len(encoded) % 4) if len(encoded) % 4 else encoded
        try:
            decoded = base64.b64decode(padded).decode('utf-8')
            print('Padded decoded:', repr(decoded))
            data = json.loads(decoded)
            print('Owner:', data.get('owner', 'NOT_FOUND'))
        except Exception as e3:
            print('Padded decode failed:', e3)
" > answer.txt 2>&1

cat answer.txt