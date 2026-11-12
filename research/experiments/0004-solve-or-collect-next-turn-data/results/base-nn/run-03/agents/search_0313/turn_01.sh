cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/base-nn/run-03/work/tasks/030_search_0313/workspace

# Decode the base64-encoded JSON and extract the owner field
cat vault/blob.txt | base64 -d | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('owner', 'NOT_FOUND'))" > answer.txt

cat answer.txt