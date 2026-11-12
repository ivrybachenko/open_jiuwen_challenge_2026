cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0005-verdict-confidence-file/results/verdict-nn/run-02/work/tasks/029_search_0229/workspace

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
def dijkstra(graph, start, end):
    if start not in graph or end not in graph:
        return None
    
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    priority_queue = [(0, start)]
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        if current_distance > distances[current_node]:
            continue
        
        if current_node == end:
            return distances[end]
        
        if current_node in graph:
            for neighbor, weight in graph[current_node]:
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(priority_queue, (distance, neighbor))
    
    return None

# Find shortest path from S to T
shortest_distance = dijkstra(graph, 'S', 'T')

if shortest_distance is not None:
    # Format the answer - if it's an integer, print as integer, otherwise as float
    if shortest_distance == int(shortest_distance):
        answer = str(int(shortest_distance))
    else:
        answer = str(shortest_distance)
else:
    answer = "No path found"

with open('answer.txt', 'w') as f:
    f.write(answer + '\n')

print(f"Shortest path weight from S to T: {answer}")
EOF