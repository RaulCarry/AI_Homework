import heapq

def Astar(initial_state, get_successors_func, is_goal_func, heuristic_func):
    pq = []
    push_order = 0 
    heapq.heappush(pq, (0, push_order, initial_state, []))

    visited = set()
    
    nodes_explored = 0
    max_memory = 0 

    while pq:
        current_memory = len(pq) + len(visited)
        if current_memory > max_memory:
            max_memory = current_memory

        f, _, current, path = heapq.heappop(pq)

        if current in visited:
            continue
        
        visited.add(current)
        nodes_explored += 1

        if is_goal_func(current):
            return path, nodes_explored

        for action, neighbor in get_successors_func(current):
            if neighbor in visited:
                continue 
            
            new_g = len(path) + 1
            h = heuristic_func(neighbor)
            
            push_order += 1
            heapq.heappush(pq, (new_g + h, push_order, neighbor, path + [action]))

    return None, nodes_explored