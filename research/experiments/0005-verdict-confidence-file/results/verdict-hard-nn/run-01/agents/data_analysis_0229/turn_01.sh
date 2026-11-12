python3 << 'EOF'
import json

with open('config.json', 'r') as f:
    data = json.load(f)

def count_numeric_leaves_greater_than_10(obj):
    count = 0
    if isinstance(obj, dict):
        for value in obj.values():
            count += count_numeric_leaves_greater_than_10(value)
    elif isinstance(obj, list):
        for item in obj:
            count += count_numeric_leaves_greater_than_10(item)
    elif isinstance(obj, bool):
        # Booleans are not numbers, so skip
        pass
    elif isinstance(obj, (int, float)):
        if obj > 10:
            count += 1
    return count

result = count_numeric_leaves_greater_than_10(data)
print(f"Count: {result}")

with open('answer.txt', 'w') as f:
    f.write(str(result) + '\n')
EOF

echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Counted numeric leaf values > 10 in nested JSON" >> verdict.txt