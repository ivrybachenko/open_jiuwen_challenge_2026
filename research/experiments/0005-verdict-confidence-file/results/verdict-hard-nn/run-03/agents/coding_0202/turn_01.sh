# Make run.sh executable and run it, capturing the output
chmod +x run.sh
output=$(bash run.sh 2>&1)
# Write the output to answer.txt with trailing newline removed
printf '%s' "$output" > answer.txt
echo "Output captured: $output"

# Create verdict.txt
echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Captured output from run.sh and wrote to answer.txt" >> verdict.txt