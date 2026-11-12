cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-02/work/tasks/028_search_0216/workspace

# Search for "Alex Morgan" in both files and extract the corresponding id
# people_new.csv has header: id,display_name
# people_old.csv has header: id,name

# Search in people_new.csv for display_name containing "Alex Morgan"
result_new=$(grep -i "Alex Morgan" people_new.csv | head -1 | cut -d',' -f1)

# Search in people_old.csv for name containing "Alex Morgan"
result_old=$(grep -i "Alex Morgan" people_old.csv | head -1 | cut -d',' -f1)

# Use whichever one is found
if [ -n "$result_new" ]; then
    echo "$result_new" > answer.txt
elif [ -n "$result_old" ]; then
    echo "$result_old" > answer.txt
else
    echo "IMPOSSIBLE: Alex Morgan not found in either file" > answer.txt
fi

cat answer.txt