cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/base-nn/run-03/work/tasks/029_search_0229/workspace

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
            source, target, weight = row[0].strip(), row[1].strip(), float(row[2].strip())
            edges.append((source, target, weight))

# Build adjacency list
adj = {}
for source, target, weight in edges:
    if source not in adj:
        adj[source] = []
    if target not in adj:
        adj[target] = []
    adj[source].append((target, weight))
    adj[target].append((source, weight))

# Dijkstra's algorithm from S to T
start = 'S'
end = 'T'

dist = {start: 0}
pq = [(0, start)]

while pq:
    d, u = heapq.heappop(pq)
    if u == end:
        print(f"Shortest path weight from {start} to {end}: {d}")
        with open('answer.txt', 'w') as f:
            f.write(str(d))
        break
    if d > dist.get(u, float('inf')):
        continue
    for v, w in adj.get(u, []):
        new_dist = d + w
        if new_dist < dist.get(v, float('inf')):
            dist[v] = new_dist
            heapq.heappush(pq, (new_dist, v))
else:
    print(f"No path found from {start} to {end}")
    with open('answer.txt', 'w') as f:
        f.write('IMPOSSIBLE')
EOF