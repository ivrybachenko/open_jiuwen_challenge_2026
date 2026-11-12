cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-nn/run-01/work/tasks/029_search_0229/workspace

python3 << 'EOF'
import csv
import heapq

# Read the graph from edges.csv
graph = {}
with open('edges.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # Skip header
    for row in reader:
        if len(row) < 3:
            continue
        source, target, weight = row[0].strip(), row[1].strip(), float(row[2].strip())
        
        if source not in graph:
            graph[source] = []
        if target not in graph:
            graph[target] = []
        
        graph[source].append((target, weight))
        graph[target].append((source, weight))

# Dijkstra's algorithm from S to T
start = 'S'
end = 'T'

# Priority queue: (distance, node)
pq = [(0, start)]
distances = {start: 0}

while pq:
    current_dist, current_node = heapq.heappop(pq)
    
    if current_node == end:
        print(f"Shortest path from {start} to {end}: {current_dist}")
        with open('answer.txt', 'w') as f:
            f.write(str(current_dist))
        break
    
    if current_dist > distances.get(current_node, float('inf')):
        continue
    
    if current_node in graph:
        for neighbor, weight in graph[current_node]:
            distance = current_dist + weight
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
else:
    print(f"No path found from {start} to {end}")
    with open('answer.txt', 'w') as f:
        f.write("IMPOSSIBLE")
EOF