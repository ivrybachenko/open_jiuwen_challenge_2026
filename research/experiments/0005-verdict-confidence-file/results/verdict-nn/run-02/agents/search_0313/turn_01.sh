cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-nn/run-02/work/tasks/030_search_0313/workspace

# Decode the base64-encoded JSON record and extract the owner
OWNER=$(base64 -d vault/blob.txt | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('owner', ''))")

# Write the answer
echo "$OWNER" > answer.txt

# Write verdict
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Extracted owner from base64-encoded JSON" >> verdict.txt