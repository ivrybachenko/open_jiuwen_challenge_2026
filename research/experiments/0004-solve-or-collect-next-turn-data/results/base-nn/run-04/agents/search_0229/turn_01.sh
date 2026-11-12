python3 << 'EOF'
import csv

# Read the edges
edges = []
with open('edges.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # Skip header
    for row in reader:
        if len(row) >= 3:
            source, target, weight = row[0].strip(), row[1].strip(), row[2].strip()
            try:
                w = float(weight)
                edges.append((source, target, w))
            except ValueError:
                pass

# Build adjacency list
from collections import defaultdict
import heapq

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
    # If it's an integer, output as integer
    if result == int(result):
        result = int(result)
    with open('answer.txt', 'w') as f:
        f.write(str(result))
    print(f"Shortest path weight: {result}")
else:
    with open('answer.txt', 'w') as f:
        f.write("IMPOSSIBLE")
    print("No path found from S to T")
EOF