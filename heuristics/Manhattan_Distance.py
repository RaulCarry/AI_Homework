
from Astar import Astar
from Sokoban import SokobanLevel, SokobanState

def heuristic(state, level):
    total_distance = 0
    for box in state.boxes:
        min_dist_to_goal = float('inf')
        for goal in level.goals:
            # Manhattan distance: |x1 - x2| + |y1 - y2|
            dist = abs(box[0] - goal[0]) + abs(box[1] - goal[1])
            if dist < min_dist_to_goal:
                min_dist_to_goal = dist
        total_distance += min_dist_to_goal
    return total_distance


    

