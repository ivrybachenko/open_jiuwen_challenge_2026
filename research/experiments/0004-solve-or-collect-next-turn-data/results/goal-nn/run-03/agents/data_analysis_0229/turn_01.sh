cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-03/work/tasks/013_data_analysis_0229/workspace

python3 -c "
import json

with open('config.json', 'r') as f:
    data = json.load(f)

def count_numeric_leaves_greater_than_10(obj):
    count = 0
    if isinstance(obj, dict):
        for v in obj.values():
            count += count_numeric_leaves_greater_than_10(v)
    elif isinstance(obj, list):
        for item in obj:
            count += count_numeric_leaves_greater_than_10(item)
    elif isinstance(obj, bool):
        # Booleans are not numbers
        pass
    elif isinstance(obj, (int, float)):
        if obj > 10:
            count += 1
    return count

result = count_numeric_leaves_greater_than_10(data)
print(f'Count: {result}')

with open('answer.txt', 'w') as f:
    f.write(str(result))
"