from collections import deque

_distance_matrix_cache = {}

def get_distance_matrix(level):
    if level in _distance_matrix_cache:
        return _distance_matrix_cache[level]

    # Map: goal -> { (x,y) -> distance }
    matrix = {}
    
    for goal in level.goals:
        distances = {}
        queue = deque([(goal, 0)])
        distances[goal] = 0
        
        while queue:
            (cx, cy), dist = queue.popleft()
            
            neighbors = [
                (cx + 1, cy), (cx - 1, cy), 
                (cx, cy + 1), (cx, cy - 1)
            ]
            
            for nx, ny in neighbors:
                if 0 <= nx < level.width and 0 <= ny < level.height:
                    if (nx, ny) not in level.walls and (nx, ny) not in distances:
                        distances[(nx, ny)] = dist + 1
                        queue.append(((nx, ny), dist + 1))
        
        matrix[goal] = distances

    _distance_matrix_cache[level] = matrix
    return matrix

def solve_assignment(box_idx, used_goals_mask, boxes, goals, cost_matrix, memo):
    # Base case: All boxes assigned
    if box_idx == len(boxes):
        return 0
    
    state_key = (box_idx, used_goals_mask)
    if state_key in memo:
        return memo[state_key]
    
    box = boxes[box_idx]
    min_cost = float('inf')
    
    for i, goal in enumerate(goals):
        if not (used_goals_mask & (1 << i)):
            
            dist = cost_matrix.get(goal, {}).get(box, float('inf'))
            
            if dist == float('inf'):
                continue
            
            remaining_cost = solve_assignment(
                box_idx + 1, 
                used_goals_mask | (1 << i), 
                boxes, 
                goals, 
                cost_matrix, 
                memo
            )
            
            if remaining_cost != float('inf'):
                total = dist + remaining_cost
                if total < min_cost:
                    min_cost = total

    memo[state_key] = min_cost
    return min_cost

def heuristic(state, level):
    matrix = get_distance_matrix(level)
    
    boxes = list(state.boxes)
    goals = list(level.goals)
    
    for box in boxes:
        can_reach_any = False
        for goal in goals:
            if box in matrix[goal]:
                can_reach_any = True
                break
        if not can_reach_any:
            return float('inf')

    memo = {}
    total_cost = solve_assignment(0, 0, boxes, goals, matrix, memo)
    
    return total_cost