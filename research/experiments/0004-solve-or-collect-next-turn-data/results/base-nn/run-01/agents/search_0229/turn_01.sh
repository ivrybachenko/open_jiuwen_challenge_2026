cat << 'EOF' > solve.py
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
                w = int(weight)
            edges.append((source, target, w))

# Build adjacency list (undirected)
adj = {}
for s, t, w in edges:
    adj.setdefault(s, []).append((t, w))
    adj.setdefault(t, []).append((s, w))

# Dijkstra from S to T
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
    for v, w in adj.get(u, []):
        nd = d + w
        if nd < dist.get(v, float('inf')):
            dist[v] = nd
            heapq.heappush(pq, (nd, v))

result = dist.get(end)
if result is None:
    print("No path found")
    result = "IMPOSSIBLE"
else:
    # If it's an integer, print as integer
    if isinstance(result, float) and result == int(result):
        result = int(result)

print(f"Shortest path weight: {result}")

with open('answer.txt', 'w') as f:
    f.write(str(result))
EOF

python3 solve.py