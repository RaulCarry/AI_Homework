import heapq

def Astar(initial_state, get_successors_func, is_goal_func, heuristic_func, limit=100000, weight=5):
    pq = []
    push_order = 0 
    heapq.heappush(pq, (0, push_order, initial_state, []))

    visited = set()
    visited.add(initial_state)
    
    nodes_explored = 0
    max_memory = 0 

    total_branching = 0
    max_branching = 0
    min_branching = float('inf')

    while pq:
        current_memory = len(pq) + len(visited)
        if current_memory > max_memory:
            max_memory = current_memory

        f, _, current, path = heapq.heappop(pq)
        
        if nodes_explored >= limit:
            print(f"   [STOP] Reached node limit: {limit}")
            avg_branching = total_branching / nodes_explored if nodes_explored > 0 else 0
            if min_branching == float('inf'): min_branching = 0
            return None, nodes_explored, max_memory, (avg_branching, max_branching, min_branching)

        nodes_explored += 1
        
        if nodes_explored % 5000 == 0:
            print(f"   [Running...] Explored {nodes_explored} nodes | Current f-score: {f}")

        if is_goal_func(current):
            avg_branching = total_branching / nodes_explored if nodes_explored > 0 else 0
            if min_branching == float('inf'): min_branching = 0
            return path, nodes_explored, max_memory, (avg_branching, max_branching, min_branching)

        successors = get_successors_func(current)
        
        num_successors = len(successors)
        total_branching += num_successors
        
        if num_successors > max_branching:
            max_branching = num_successors
        if num_successors < min_branching:
            min_branching = num_successors

        for action, neighbor in successors:
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

    avg_branching = total_branching / nodes_explored if nodes_explored > 0 else 0
    if min_branching == float('inf'): min_branching = 0
    return None, nodes_explored, max_memory, (avg_branching, max_branching, min_branching)