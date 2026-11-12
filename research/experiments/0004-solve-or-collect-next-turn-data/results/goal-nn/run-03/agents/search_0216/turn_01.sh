cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-03/work/tasks/028_search_0216/workspace

# Search for "Alex Morgan" in both files and extract the corresponding id
# Check people_new.csv (header: id,display_name)
id_new=$(grep -i "Alex Morgan" people_new.csv | head -1 | cut -d',' -f1)

# Check people_old.csv (header: id,name)
id_old=$(grep -i "Alex Morgan" people_old.csv | head -1 | cut -d',' -f1)

# Determine which one has the match
if [ -n "$id_new" ]; then
    echo "$id_new" > answer.txt
    echo "Found in people_new.csv: $id_new"
elif [ -n "$id_old" ]; then
    echo "$id_old" > answer.txt
    echo "Found in people_old.csv: $id_old"
else
    echo "IMPOSSIBLE" > answer.txt
    echo "Alex Morgan not found in either file"
fi