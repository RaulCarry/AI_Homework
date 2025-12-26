from collections import deque

_distance_cache = {}

def compute_distance_map(level):
    distances = {}
    queue = deque()

    for goal in level.goals:
        distances[goal] = 0
        queue.append(goal)

    while queue:
        x, y = queue.popleft()
        current_dist = distances[(x, y)]

        neighbors = [
            (x + 1, y), (x - 1, y), 
            (x, y + 1), (x, y - 1)
        ]
        
        for nx, ny in neighbors:
            if 0 <= nx < level.width and 0 <= ny < level.height:
                if (nx, ny) not in level.walls and (nx, ny) not in distances:
                    distances[(nx, ny)] = current_dist + 1
                    queue.append((nx, ny))
    
    return distances

def heuristic(state, level):
    #Lazy-load the distance map for this specific level
    if level not in _distance_cache:
        _distance_cache[level] = compute_distance_map(level)
    
    distances = _distance_cache[level]
    total_cost = 0

    for box in state.boxes:
        if box in distances:
            total_cost += distances[box]
        else:
            return float('inf')
            
    return total_cost