import time
import os 
import subprocess
from Sokoban import SokobanLevel
from Astar import Astar
import heristics.Real_Maze_Distance as Real_Maze_Distance
import heristics.New_Real_Maze_Distance as New_Real_Maze_Distance
import heristics.Fast_Distance as Fast_Distance
import heristics.Exact_Distance as Exact_Distance
import heristics.Satificing as Satificing
from pddl.PDDL_Generator import PDDLGenerator

level_number=1
PLANNER_PATH = "fast-downward/fast-downward.py"
DOMAIN_PATH = "pddl/domain.pddl"

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

def run_fast_downward(domain_file, problem_file, time_limit=60):
    print(f"   [Planner] Running Fast Downward on {problem_file}...")

    if not os.path.exists(domain_file):
        print(f"      [ERROR] Domain file '{domain_file}' not found.")
        return

    cmd = [
        PLANNER_PATH,
        "--alias", "seq-opt-lmcut", 
        "--overall-time-limit", str(time_limit),
        domain_file,
        problem_file
    ]

    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        end_time = time.time()
        duration = end_time - start_time
        
        if os.path.exists("sas_plan"):
            with open("sas_plan", "r") as f:
                plan_lines = f.readlines()
            
            plan = [line.strip() for line in plan_lines if not line.startswith(";")]
            
            os.remove("sas_plan")
            
            print(f"      [SUCCESS] Time: {duration:.4f}s | Plan Length: {len(plan)}")
            return plan, duration
        else:
            print(f"      [FAILED] Planner finished but no 'sas_plan' found.")

            print("      [PLANNER OUTPUT]:")
            print(result.stdout)  
            print("      [PLANNER ERROR]:")
            print(result.stderr)  
            # --------------------------
            return None, duration

    except FileNotFoundError:
        print(f"      [ERROR] Could not find planner at: {PLANNER_PATH}")
        return None, 0
    
    
    
def solve_level(level_index):
    levels = parse_levels('sokoban_levels.txt')
    if level_index >= len(levels): return

    level_str = levels[level_index]
    print(f"\n=== SOLVING LEVEL {level_index + 1} ===")
    level = SokobanLevel(level_str)
    print(level.print_state(level.initial_state))
    print("-" * 30)
    
    pddl_gen = PDDLGenerator(level, level_name=f"level{level_index+1}")
    pddl_gen.write_to_file(f"problem_{level_number}.pddl")
    print("PDDL generated successfully.")

    run_fast_downward(f"domain.pddl", f"problem_{level_number}.pddl")
    
    run_astar(level, Satificing.heuristic)

if __name__ == "__main__":
    solve_level(level_number) 