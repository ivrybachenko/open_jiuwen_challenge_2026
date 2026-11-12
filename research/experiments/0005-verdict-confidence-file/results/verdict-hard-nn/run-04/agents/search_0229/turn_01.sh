cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-hard-nn/run-04/work/tasks/029_search_0229/workspace

python3 << 'EOF'
import csv
import heapq

# Read edges
edges = []
with open('edges.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # skip header
    for row in reader:
        if len(row) >= 3:
            source, target, weight = row[0].strip(), row[1].strip(), row[2].strip()
            try:
                w = float(weight)
            except ValueError:
                continue
            edges.append((source, target, w))

# Build adjacency list
from collections import defaultdict
adj = defaultdict(list)
for s, t, w in edges:
    adj[s].append((t, w))
    adj[t].append((s, w))

# Dijkstra's algorithm from S to T
start = 'S'
end = 'T'

dist = {start: 0}
pq = [(0, start)]

while pq:
    d, u = heapq.heappop(pq)
    if d > dist.get(u, float('inf')):
        continue
    if u == end:
        break
    for v, w in adj[u]:
        new_dist = d + w
        if new_dist < dist.get(v, float('inf')):
            dist[v] = new_dist
            heapq.heappush(pq, (new_dist, v))

if end in dist:
    result = dist[end]
    # If it's an integer, print as integer
    if result == int(result):
        result = int(result)
    print(f"Shortest path weight: {result}")
    with open('answer.txt', 'w') as f:
        f.write(str(result))
else:
    print("No path found from S to T")
    with open('answer.txt', 'w') as f:
        f.write("IMPOSSIBLE")

EOF

echo "solved" > verdict.txt
echo "1.00" >> verdict.txt
echo "Computed shortest path using Dijkstra" >> verdict.txt