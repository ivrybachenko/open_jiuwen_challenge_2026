cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-hard-nn/run-01/work/tasks/030_search_0313/workspace

# Decode the base64-encoded JSON record and extract the owner field
cat vault/blob.txt | base64 -d | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('owner', 'NOT_FOUND'))" > answer.txt

# Verify the answer
cat answer.txt

# Create verdict.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Extracted owner from base64-encoded JSON" >> verdict.txt