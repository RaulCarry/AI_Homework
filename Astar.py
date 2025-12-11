import heapq

def Astar(initial_state, get_successors_func, is_goal_func, heuristic_func):
    
    pq = []
    heapq.heappush(pq, (0, 0, initial_state, []))

    visited = {initial_state: 0}
    nodes_explored = 0

    while pq:
        f, _, current, path = heapq.heappop(pq)
        nodes_explored += 1

        if is_goal_func(current):
            return path, nodes_explored

        if visited[current] < len(path):
            continue

        for action, neighbor in get_successors_func(current):
            new_g = len(path) + 1
            
            if neighbor not in visited or new_g < visited[neighbor]:
                visited[neighbor] = new_g
                h = heuristic_func(neighbor)
                heapq.heappush(pq, (new_g + h, nodes_explored, neighbor, path + [action]))

    return None, nodes_explored