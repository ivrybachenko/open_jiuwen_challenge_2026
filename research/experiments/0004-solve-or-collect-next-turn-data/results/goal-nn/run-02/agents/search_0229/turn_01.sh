cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-02/work/tasks/029_search_0229/workspace

python3 << 'EOF'
import csv
import heapq

# Read the edges
edges = []
with open('edges.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # Skip header
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
def dijkstra(adj, start, end):
    if start not in adj or end not in adj:
        return None
    
    dist = {start: 0}
    pq = [(0, start)]
    
    while pq:
        current_dist, current_node = heapq.heappop(pq)
        
        if current_node == end:
            return current_dist
        
        if current_dist > dist.get(current_node, float('inf')):
            continue
        
        for neighbor, weight in adj.get(current_node, []):
            distance = current_dist + weight
            if distance < dist.get(neighbor, float('inf')):
                dist[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    
    return None

result = dijkstra(adj, 'S', 'T')
print(f"Shortest path weight from S to T: {result}")

with open('answer.txt', 'w') as f:
    f.write(str(result))
EOF