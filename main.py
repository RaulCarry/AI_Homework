import time
from Sokoban import SokobanLevel
from Astar import Astar
import Real_Maze_Distance
import New_Real_Maze_Distance
import Fast_Distance
import Exact_Distance
import Satificing

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

def run_astar(level, heuristic_func):
    print(f"   [1] Running Weighted {heuristic_func}...")
    
    def get_neighbors(state): return SokobanLevel.get_successors(state, level)
    def is_goal(state): return SokobanLevel.is_goal(state, level)
    def h_func(state): return heuristic_func(state, level)

    start = time.time()
    path, nodes = Astar(level.initial_state, get_neighbors, is_goal, h_func, limit=20000000, weight=3.0)
    end = time.time()
    
    if path:
        print(f"      [SUCCESS] Time: {end-start:.4f}s | Nodes: {nodes} | Len: {len(path)}")
    else:
        print(f"      [FAILED] Time: {end-start:.4f}s | Nodes: {nodes}")

def solve_level(level_index):
    levels = parse_levels('sokoban_levels.txt')
    if level_index >= len(levels): return

    level_str = levels[level_index]
    print(f"\n=== SOLVING LEVEL {level_index + 1} ===")
    level = SokobanLevel(level_str)
    print(level.print_state(level.initial_state))
    print("-" * 30)

    run_astar(level, Satificing.heuristic)

if __name__ == "__main__":
    solve_level(1) 