from collections import deque

_dist_cache = {}

def get_distances(level):
    if level in _dist_cache: return _dist_cache[level]
    goals_map = {}
    for goal in level.goals:
        q = deque([(goal, 0)])
        visited = {goal}
        dists = {goal: 0}
        
        while q:
            (cx, cy), d = q.popleft()
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                nx, ny = cx+dx, cy+dy
                
                if 0 <= nx < level.width and 0 <= ny < level.height:
                    if (nx, ny) not in level.walls and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        dists[(nx, ny)] = d + 1
                        q.append(((nx, ny), d + 1))
                        
        goals_map[goal] = dists
    
    _dist_cache[level] = goals_map
    return goals_map

def heuristic(state, level):
    goals_map = get_distances(level)
    
    boxes = list(state.boxes)
    goals = list(level.goals)
    edges = []
    
    for b_i, box in enumerate(boxes):
        for g_i, goal in enumerate(goals):
            if box in goals_map[goal]:
                d = goals_map[goal][box]
                edges.append((d, b_i, g_i))
            else:
                pass
    
    edges.sort(key=lambda x: x[0])
    
    total_cost = 0
    assigned_boxes = set()
    assigned_goals = set()
    matches = 0
    
    for dist, b_i, g_i in edges:
        if b_i not in assigned_boxes and g_i not in assigned_goals:
            assigned_boxes.add(b_i)
            assigned_goals.add(g_i)
            total_cost += dist
            matches += 1
            
    if matches < len(boxes):
        return float('inf')
        
    return total_cost