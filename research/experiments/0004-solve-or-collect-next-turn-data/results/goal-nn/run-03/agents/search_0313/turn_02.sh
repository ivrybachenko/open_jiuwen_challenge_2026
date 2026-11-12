cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-03/work/tasks/030_search_0313/workspace

# First, let's see what the raw blob.txt contains and what base64 decoding produces
echo "=== Raw blob.txt ==="
cat vault/blob.txt
echo ""
echo "=== Base64 decoded ==="
base64 -d < vault/blob.txt 2>/dev/null || echo "base64 decode failed"
echo ""
echo "=== Try with python base64 ==="
python3 -c "
import base64, json, sys
with open('vault/blob.txt', 'r') as f:
    encoded = f.read().strip()
try:
    decoded = base64.b64decode(encoded)
    print('Decoded bytes:', decoded)
    print('Decoded str:', decoded.decode('utf-8'))
    try:
        data = json.loads(decoded)
        print('JSON owner:', data.get('owner', 'NO OWNER KEY'))
    except json.JSONDecodeError as e:
        print('JSON error:', e)
except Exception as e:
    print('Decode error:', e)
" > answer.txt 2>&1

cat answer.txt