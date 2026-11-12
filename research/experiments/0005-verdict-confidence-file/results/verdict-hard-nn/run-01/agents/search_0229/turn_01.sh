cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-hard-nn/run-01/work/tasks/029_search_0229/workspace

python3 << 'EOF'
import csv
import heapq

# Read edges from edges.csv
edges = []
with open('edges.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # Skip header
    for row in reader:
        if len(row) >= 3:
            source, target, weight = row[0].strip(), row[1].strip(), row[2].strip()
            try:
                w = int(weight)
            except ValueError:
                try:
                    w = float(weight)
                except ValueError:
                    continue
            edges.append((source, target, w))

# Build adjacency list for undirected graph
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

# Check if start and end exist
if start not in adj or end not in adj:
    print(f"Error: {start} or {end} not found in graph")
    with open('answer.txt', 'w') as f:
        f.write('IMPOSSIBLE')
    with open('verdict.txt', 'w') as f:
        f.write('impossible\n0.00\nStart or end node not found in graph\n')
    exit()

# Dijkstra
dist = {start: 0}
pq = [(0, start)]
visited = set()

while pq:
    d, u = heapq.heappop(pq)
    if u in visited:
        continue
    visited.add(u)
    if u == end:
        break
    if u in adj:
        for v, w in adj[u]:
            new_dist = d + w
            if v not in dist or new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(pq, (new_dist, v))

if end in dist:
    answer = dist[end]
    # Format: if integer, print as integer, else as float
    if isinstance(answer, float) and answer == int(answer):
        answer = int(answer)
    print(f"Shortest path weight from S to T: {answer}")
    with open('answer.txt', 'w') as f:
        f.write(str(answer))
else:
    print("No path from S to T")
    with open('answer.txt', 'w') as f:
        f.write('IMPOSSIBLE')
    with open('verdict.txt', 'w') as f:
        f.write('impossible\n0.00\nNo path from S to T\n')
    exit()

with open('verdict.txt', 'w') as f:
    f.write('solved\n1.00\nShortest path computed using Dijkstra\n')
EOF