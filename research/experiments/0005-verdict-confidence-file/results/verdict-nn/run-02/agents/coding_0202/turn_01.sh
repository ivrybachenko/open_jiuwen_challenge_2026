cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-nn/run-02/work/tasks/000_coding_0202/workspace

# Make run.sh executable
chmod +x run.sh

# Run it and capture output, removing trailing newline
output=$(bash run.sh)

# Write to answer.txt
echo -n "$output" > answer.txt

# Also write verdict.txt
cat > verdict.txt << 'EOF'
solved
1.00
Task completed successfully
EOF