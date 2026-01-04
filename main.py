import time
import os 
import subprocess
import csv
import re
from Sokoban import SokobanLevel
from Astar import Astar
import heristics.Real_Maze_Distance as Real_Maze_Distance
import heristics.New_Real_Maze_Distance as New_Real_Maze_Distance
import heristics.Fast_Distance as Fast_Distance
import heristics.Exact_Distance as Exact_Distance
import heristics.Satificing as Satificing
from pddl.PDDL_Generator import PDDLGenerator

level_number = 1
PLANNER_PATH = "fast-downward/fast-downward.py"
PLANNER_PATH2 = "./lama-first"
DOMAIN_PATH = "pddl/domain.pddl"


LOG_FILE = "experiment_log.txt"
CSV_FILE = "experiment_data.csv"

def log(message):
    print(message)
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

def log_csv(algorithm, level_id, status, duration, metric_type, metric_value):
    """Writes a row of data to a CSV file for easy plotting."""
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Algorithm", "Level", "Status", "Time (s)", "Metric Type", "Metric Value"])
        writer.writerow([algorithm, level_id, status, f"{duration:.4f}", metric_type, metric_value])

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
        if current_level_lines:
            levels.append("".join(current_level_lines))
    return levels

def run_astar(level, heuristic_func, level_id):
    algo_name = f"A* ({heuristic_func.__module__.split('.')[-1]})"
    log(f"   [1] Running {algo_name}...")
    
    def get_neighbors(state): return SokobanLevel.get_successors(state, level)
    def is_goal(state): return SokobanLevel.is_goal(state, level)
    def h_func(state): return heuristic_func(state, level)

    start = time.time()
    path, nodes, mem = Astar(level.initial_state, get_neighbors, is_goal, h_func, limit=20000000, weight=3.0)
    end = time.time()
    duration = end - start
    
    log_csv(algo_name, level_id, "Memory", duration, "Max Stored Nodes", mem)
    
    if path:
        log(f"      [SUCCESS] Time: {duration:.4f}s | Nodes: {nodes} | Mem: {mem} | Len: {len(path)}")
        log_csv(algo_name, level_id, "SUCCESS", duration, "Nodes Expanded", nodes)
    else:
        log(f"      [FAILED] Time: {duration:.4f}s | Nodes: {nodes} | Mem: {mem}")
        log_csv(algo_name, level_id, "FAILED", duration, "Nodes Expanded", nodes)
        
        

def run_fast_downward(domain_file, problem_file, level_id, time_limit=300):
    log(f"   [Planner] Running Fast Downward on {problem_file}...")

    if not os.path.exists(domain_file):
        log(f"      [ERROR] Domain file '{domain_file}' not found.")
        return

    cmd = [
        PLANNER_PATH,
        "--overall-time-limit", str(time_limit),
        domain_file,
        problem_file,
        "--search", "lazy_greedy([ff()], preferred=[ff()])"
    ]

    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        duration = time.time() - start_time

        nodes_expanded = 0
        nodes_match = re.search(r"Expanded (\d+) state\(s\)", result.stdout)
        if nodes_match:
            nodes_expanded = int(nodes_match.group(1))
        
        log_csv("Fast Downward", level_id, "Metrics", duration, "Nodes Expanded", nodes_expanded)
        
        if os.path.exists("sas_plan"):
            with open("sas_plan", "r") as f:
                plan_lines = f.readlines()
            
            plan = [line.strip() for line in plan_lines if not line.startswith(";")]
            os.remove("sas_plan")
            
            log(f"      [SUCCESS] Time: {duration:.4f}s | Nodes: {nodes_expanded} | Plan Length: {len(plan)}")
            log_csv("Fast Downward", level_id, "SUCCESS", duration, "Plan Length", len(plan))
            return plan, duration
        else:
            log("      [FAILED] Planner finished but no 'sas_plan' found.")
            log("      [PLANNER OUTPUT]:")
            log(result.stdout)
            log("      [PLANNER ERROR]:")
            log(result.stderr)
            log_csv("Fast Downward", level_id, "FAILED", duration, "Plan Length", 0)
            return None, duration

    except FileNotFoundError:
        log(f"      [ERROR] Could not find planner at: {PLANNER_PATH}")
        return None, 0
    
def run_lama_first(domain_file, problem_file, level_id, time_limit=300):
    log(f"   [Planner] Running {PLANNER_PATH2} on {problem_file}...")

    cmd = [PLANNER_PATH2, domain_file, problem_file]

    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            timeout=time_limit
        )
        duration = time.time() - start_time
        
        plan_files = [f for f in os.listdir('.') if f.startswith('sas_plan') and not f.endswith('.pddl')]
        
        if plan_files:
            plan_files.sort()
            best_plan_file = plan_files[-1]
            
            with open(best_plan_file, "r") as f:
                plan_lines = f.readlines()
            
            for f in plan_files:
                os.remove(f)

            plan = [line.strip() for line in plan_lines if not line.startswith(";")]
            log(f"      [SUCCESS] Time: {duration:.4f}s | Plan Length: {len(plan)}")
            log_csv("LAMA First", level_id, "SUCCESS", duration, "Plan Length", len(plan))
            return plan, duration
        else: 
            log("      [PLANNER OUTPUT]:")
            log(result.stdout)
            log("      [PLANNER ERROR]:")
            log(result.stderr)
            
            log_csv("LAMA First", level_id, "FAILED", duration, "Plan Length", 0)
            return None, duration

    except subprocess.TimeoutExpired:
        log(f"      [FAILED] Planner timed out after {time_limit} seconds.")
        log_csv("LAMA First", level_id, "TIMEOUT", time_limit, "Plan Length", 0)
        return None, time_limit
    except FileNotFoundError:
        log(f"      [ERROR] Command '{PLANNER_PATH2}' not found.")
        return None, 0
    
def solve_level(level_index):
    levels = parse_levels('ez_level.txt')
    if level_index >= len(levels): 
        print(f"Level index {level_index} out of range.")
        return

    level_str = levels[level_index]
    level_id = f"Level {level_index}"
    
    log(f"\n=== SOLVING {level_id} ===")
    level = SokobanLevel(level_str)
    log(level.print_state(level.initial_state))
    log("-" * 30)
    
    pddl_gen = PDDLGenerator(level, level_name=f"level{level_index}")
    problem_filename = f"problem_{level_index}.pddl"
    pddl_gen.write_to_file(problem_filename)
    log("PDDL generated successfully.")

    run_lama_first(f"domain.pddl", problem_filename, level_id)
    run_fast_downward(f"domain.pddl", problem_filename, level_id)
    run_astar(level, Satificing.heuristic, level_id)

if __name__ == "__main__":

    with open(LOG_FILE, "w") as f:
        f.write("--- NEW EXPERIMENT SESSION ---\n")
    
    levels = parse_levels('ez_level.txt') 
    
    for i in range(len(levels)):
        solve_level(i)