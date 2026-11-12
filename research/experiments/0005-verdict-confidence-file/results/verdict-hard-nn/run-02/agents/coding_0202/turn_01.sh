cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-hard-nn/run-02/work/tasks/000_coding_0202/workspace

# Make run.sh executable
chmod +x run.sh

# Run it and capture output, removing trailing newline
output=$(bash run.sh)

# Write to answer.txt
echo "$output" > answer.txt

# Create verdict.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "run.sh was made executable and its output was captured and written to answer.txt" >> verdict.txt