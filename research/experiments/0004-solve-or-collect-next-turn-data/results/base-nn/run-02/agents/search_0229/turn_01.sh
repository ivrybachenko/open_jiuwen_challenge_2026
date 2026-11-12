cat << 'EOF' > solve.py
import csv
import heapq

# Read edges
edges = []
with open('edges.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        src = row['source']
        tgt = row['target']
        weight = int(row['weight'])
        edges.append((src, tgt, weight))

# Build adjacency list
adj = {}
for src, tgt, weight in edges:
    if src not in adj:
        adj[src] = []
    if tgt not in adj:
        adj[tgt] = []
    adj[src].append((tgt, weight))
    adj[tgt].append((src, weight))

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
        print(d)
        with open('answer.txt', 'w') as f:
            f.write(str(d))
        break
    if u in adj:
        for v, w in adj[u]:
            new_dist = d + w
            if new_dist < dist.get(v, float('inf')):
                dist[v] = new_dist
                heapq.heappush(pq, (new_dist, v))
else:
    print("No path found")
    with open('answer.txt', 'w') as f:
        f.write("NO_PATH")
EOF

python3 solve.py