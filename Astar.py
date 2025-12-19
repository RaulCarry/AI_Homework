import heapq


def Astar(initial_state, get_successors_func, is_goal_func, heuristic_func, limit=100000, weight=5):
    pq = []
    push_order = 0 
    heapq.heappush(pq, (0, push_order, initial_state, []))

    visited = set()
    visited.add(initial_state)
    
    nodes_explored = 0
    max_memory = 0 

    while pq:
        if nodes_explored >= limit:
            print(f"   [STOP] Reached node limit: {limit}")
            return None, nodes_explored

        current_memory = len(pq) + len(visited)
        if current_memory > max_memory:
            max_memory = current_memory

        f, _, current, path = heapq.heappop(pq)
        nodes_explored += 1
        
        if nodes_explored % 5000 == 0:
            print(f"   [Running...] Explored {nodes_explored} nodes | Current f-score: {f}")

        if is_goal_func(current):
            return path, nodes_explored

        for action, neighbor in get_successors_func(current):
            if neighbor in visited:
                continue 
            
            visited.add(neighbor)
            
            new_g = len(path) + 1
            h = heuristic_func(neighbor)
            
            if h == float('inf'):
                continue

            f_score = new_g + (weight * h)
            
            push_order += 1
            heapq.heappush(pq, (f_score, push_order, neighbor, path + [action]))

    return None, nodes_explored