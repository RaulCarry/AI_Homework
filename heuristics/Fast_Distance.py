from collections import deque

_level_cache = {}

def get_min_distance_map(level):
    if level in _level_cache:
        return _level_cache[level]

    min_distances = {}
    queue = deque()
    
    for goal in level.goals:
        queue.append((goal, 0))
        min_distances[goal] = 0
        
    visited = set(level.goals)

    while queue:
        (cx, cy), dist = queue.popleft()
        
        neighbors = [
            (cx + 1, cy), (cx - 1, cy), 
            (cx, cy + 1), (cx, cy - 1)
        ]
        
        for nx, ny in neighbors:
            if 0 <= nx < level.width and 0 <= ny < level.height:
                if (nx, ny) not in level.walls and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    min_distances[(nx, ny)] = dist + 1
                    queue.append(((nx, ny), dist + 1))
    
    _level_cache[level] = min_distances
    return min_distances

def heuristic(state, level):
    min_dists = get_min_distance_map(level)
    total_cost = 0
    
    for box in state.boxes:
        if box in min_dists:
            total_cost += min_dists[box]
        else:
            return float('inf')
            
    return total_cost