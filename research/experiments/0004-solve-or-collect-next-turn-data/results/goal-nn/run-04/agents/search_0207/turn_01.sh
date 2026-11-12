cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-04/work/tasks/026_search_0207/workspace

# Extract the port value from the [server] section of config.ini
PORT=$(grep -A 10 '^\[server\]' config.ini | grep -i 'port' | head -1 | sed 's/.*=\s*//' | tr -d '[:space:]')

echo "Extracted port: $PORT"
echo "$PORT" > answer.txt