import numpy as np
from scipy.optimize import linear_sum_assignment
from collections import deque

_maze_cache = {}

def get_bfs_matrix(level):
    if level in _maze_cache:
        return _maze_cache[level]

    matrix = {}
    for goal in level.goals:
        distances = {}
        queue = deque([(goal, 0)])
        visited = {goal}
        distances[goal] = 0
        while queue:
            (cx, cy), dist = queue.popleft()
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < level.width and 0 <= ny < level.height:
                    if (nx, ny) not in level.walls and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        distances[(nx, ny)] = dist + 1
                        queue.append(((nx, ny), dist + 1))
        matrix[goal] = distances
    _maze_cache[level] = matrix
    return matrix

def heuristic(state, level):
    # Safe access via .boxes again
    boxes = list(state.boxes)
    goals = list(level.goals)
    
    bfs_matrix = get_bfs_matrix(level)
    cost_matrix = np.zeros((len(boxes), len(goals)))
    
    for i, box in enumerate(boxes):
        for j, goal in enumerate(goals):
            if box in bfs_matrix[goal]:
                cost_matrix[i, j] = bfs_matrix[goal][box]
            else:
                cost_matrix[i, j] = 100000 

    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    total_dist = cost_matrix[row_ind, col_ind].sum()
    
    if total_dist >= 100000:
        return float('inf')
        
    return total_dist