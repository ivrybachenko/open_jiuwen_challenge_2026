cat << 'EOF' > solve.py
import csv
import heapq

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
                # Check if it's an integer
                if w == int(w):
                    w = int(w)
                edges.append((source, target, w))
            except ValueError:
                continue

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
    visited = set()
    
    while pq:
        current_dist, current_node = heapq.heappop(pq)
        
        if current_node in visited:
            continue
        visited.add(current_node)
        
        if current_node == end:
            return current_dist
        
        if current_node in adj:
            for neighbor, weight in adj[current_node]:
                if neighbor not in visited:
                    new_dist = current_dist + weight
                    if neighbor not in dist or new_dist < dist[neighbor]:
                        dist[neighbor] = new_dist
                        heapq.heappush(pq, (new_dist, neighbor))
    
    return None

result = dijkstra(adj, 'S', 'T')

if result is not None:
    # If it's an integer, print as integer
    if isinstance(result, float) and result == int(result):
        result = int(result)
    print(result)
    with open('answer.txt', 'w') as f:
        f.write(str(result) + '\n')
else:
    print("No path found")
    with open('answer.txt', 'w') as f:
        f.write("NO_PATH\n")

EOF

python3 solve.py