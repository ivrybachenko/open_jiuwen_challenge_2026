python3 << 'EOF'
import csv

# Read the edges
edges = []
with open('edges.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # Skip header
    for row in reader:
        if len(row) >= 3:
            source, target, weight = row[0], row[1], float(row[2])
            edges.append((source, target, weight))

# Build adjacency list
from collections import defaultdict
import heapq

adj = defaultdict(list)
for source, target, weight in edges:
    adj[source].append((target, weight))
    adj[target].append((source, weight))

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
    print(f"Shortest path weight from S to T: {dist[end]}")
    with open('answer.txt', 'w') as f:
        f.write(str(dist[end]))
else:
    print("No path found from S to T")
    with open('answer.txt', 'w') as f:
        f.write("IMPOSSIBLE")
EOF