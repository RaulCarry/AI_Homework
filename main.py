import time
from Sokoban import SokobanLevel
from Astar import Astar
from Manhattan_Distance import heuristic

def parse_levels(filename):
    levels = []
    current_level_lines = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith("Title:") or line.startswith("Author:") or line.startswith("Comment:"):
                if current_level_lines:
                    levels.append("".join(current_level_lines))
                    current_level_lines = []
            elif line.strip() == "":
                continue 
            else:
                current_level_lines.append(line)
    return levels


def solve_level(level_index):
    levels = parse_levels('sokoban_levels.txt')
    if level_index >= len(levels):
        print(f"Level {level_index} not found.")
        return

    level_string = levels[level_index]
    print(f"--- Loading: {level_index + 1} ---")
    
    level = SokobanLevel(level_string)
    print(level.print_state(level.initial_state))
    print("\nPlaying it...")

    def get_neighbors_wrapper(state):
        return SokobanLevel.get_successors(state, level)

    def is_goal_wrapper(state):
        return SokobanLevel.is_goal(state, level)

    def heuristic_wrapper(state):
        return heuristic(state, level)

    start_time = time.time()
    path, nodes_explored = Astar(
        level.initial_state,
        get_neighbors_wrapper,
        is_goal_wrapper,
        heuristic_wrapper
    )
    end_time = time.time()

    if path:
        print(f"\nSolution found in {end_time - start_time:.4f} seconds.")
        print(f"Nodes explored: {nodes_explored}")
        print(f"Path length: {len(path)}")
        print(f"Path: {path}")
    else:
        print("\nNo solution found.")

if __name__ == "__main__":
    solve_level(0)