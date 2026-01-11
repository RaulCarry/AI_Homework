import time
import os 
import subprocess
import csv
import re
from Sokoban import SokobanLevel
from Astar import Astar
import heuristics.Manhattan_Distance as Manhattan_Distance
import heuristics.Real_Maze_Distance as Real_Maze_Distance
import heuristics.New_Real_Maze_Distance as New_Real_Maze_Distance
import heuristics.Hungarian_BFS as Hungarian_Distance
import heuristics.Fast_Distance as Fast_Distance
import heuristics.Exact_Distance as Exact_Distance
import heuristics.Satificing as Satificing
from pddl.PDDL_Generator import PDDLGenerator

LEVELS_FILE = "ez_level.txt"
PLANNER_PATH = "fast-downward/fast-downward.py" 
PLANNER_PATH2 = "./lama-first"                  
DOMAIN_PATH = "pddl/domain.pddl"
LOG_FILE = "experiment_log_ez.txt"
CSV_FILE = "experiment_data_ez.csv"
TIME_LIMIT = 60 

def log(message):
    print(message)
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

def log_csv(algorithm, level_id, status, duration, metric_type, metric_value):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Algorithm", "Level", "Status", "Time (s)", "Metric Type", "Metric Value"])
        writer.writerow([algorithm, level_id, status, f"{duration:.4f}", metric_type, metric_value])

def parse_levels(filename):
    levels = []
    current_level_lines = []
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return []
        
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith(";"): 
                continue
            if line.startswith("Title:") or line.startswith("Author:") or line.startswith("Comment:"):
                if current_level_lines:
                    levels.append("".join(current_level_lines))
                    current_level_lines = []
            elif line.strip() == "":
                if current_level_lines:
                    levels.append("".join(current_level_lines))
                    current_level_lines = []
            else:
                current_level_lines.append(line)
        if current_level_lines:
            levels.append("".join(current_level_lines))
    return levels

def run_astar(level, heuristic_func, heuristic_name, level_id):
    algo_name = f"A* ({heuristic_name})"
    log(f"   [1] Running {algo_name}...")
    
    def get_neighbors(state): return SokobanLevel.get_successors(state, level)
    def is_goal(state): return SokobanLevel.is_goal(state, level)
    def h_func(state): return heuristic_func(state, level)

    start = time.time()
    result = Astar(level.initial_state, get_neighbors, is_goal, h_func, limit=500000, weight=3.0)
    end = time.time()
    duration = end - start
    
    path, nodes, mem, branching_stats = result
    avg_b, max_b, min_b = branching_stats
    
    log_csv(algo_name, level_id, "Memory", duration, "Max Stored Nodes", mem)
    log_csv(algo_name, level_id, "Branching", duration, "Avg Branching", avg_b)
    log_csv(algo_name, level_id, "Branching", duration, "Max Branching", max_b)

    if path:
        log(f"      [SUCCESS] Time: {duration:.4f}s | Nodes: {nodes} | Mem: {mem} | Avg Branch: {avg_b:.2f} | Len: {len(path)}")
        log_csv(algo_name, level_id, "SUCCESS", duration, "Nodes Expanded", nodes)
        log_csv(algo_name, level_id, "SUCCESS", duration, "Solution Length", len(path))
    else:
        log(f"      [FAILED] Time: {duration:.4f}s | Nodes: {nodes} | Mem: {mem}")
        log_csv(algo_name, level_id, "FAILED", duration, "Nodes Expanded", nodes)

def run_fast_downward(domain_file, problem_file, level_id, time_limit=300):
    algo_name = "Fast Downward"
    log(f"   [Planner] Running {algo_name} on {problem_file}...")

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
        nodes_generated = 0
        
        expanded_matches = re.findall(r"Expanded (\d+) state\(s\)", result.stdout)
        generated_matches = re.findall(r"Generated (\d+) state\(s\)", result.stdout)
        
        if expanded_matches:
            nodes_expanded = sum(int(x) for x in expanded_matches)
        if generated_matches:
            nodes_generated = sum(int(x) for x in generated_matches)

        avg_branching = 0
        if nodes_expanded > 0:
            avg_branching = nodes_generated / nodes_expanded

        log_csv(algo_name, level_id, "Metrics", duration, "Nodes Expanded", nodes_expanded)
        log_csv(algo_name, level_id, "Branching", duration, "Avg Branching", avg_branching)
        
        if os.path.exists("sas_plan"):
            with open("sas_plan", "r") as f:
                plan_lines = f.readlines()
            
            plan = [line.strip() for line in plan_lines if not line.startswith(";")]
            os.remove("sas_plan") 
            
            log(f"      [SUCCESS] Time: {duration:.4f}s | Nodes: {nodes_expanded} | Branch: {avg_branching:.2f} | Plan Len: {len(plan)}")
            log_csv(algo_name, level_id, "SUCCESS", duration, "Solution Length", len(plan))
            return plan, duration
        else:
            log(f"      [FAILED] No plan found (Exit code {result.returncode}).")
            log_csv(algo_name, level_id, "FAILED", duration, "Solution Length", 0)
            return None, duration

    except FileNotFoundError:
        log(f"      [ERROR] Could not find planner executable at: {PLANNER_PATH}")
        return None, 0

def run_lama_first(domain_file, problem_file, level_id, time_limit=300):
    algo_name = "LAMA First"
    log(f"   [Planner] Running {algo_name} on {problem_file}...")

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
        
        nodes_expanded = 0
        nodes_generated = 0
        
        expanded_matches = re.findall(r"Expanded (\d+) state\(s\)", result.stdout)
        generated_matches = re.findall(r"Generated (\d+) state\(s\)", result.stdout)
        
        if expanded_matches:
            nodes_expanded = sum(int(x) for x in expanded_matches)
        if generated_matches:
            nodes_generated = sum(int(x) for x in generated_matches)
            
        avg_branching = 0
        if nodes_expanded > 0:
            avg_branching = nodes_generated / nodes_expanded

        log_csv(algo_name, level_id, "Metrics", duration, "Nodes Expanded", nodes_expanded)
        log_csv(algo_name, level_id, "Branching", duration, "Avg Branching", avg_branching)
        
        plan_files = [f for f in os.listdir('.') if f.startswith('sas_plan') and not f.endswith('.pddl')]
        
        if plan_files:
            plan_files.sort()
            best_plan_file = plan_files[-1]
            
            with open(best_plan_file, "r") as f:
                plan_lines = f.readlines()
            
            for f in plan_files:
                os.remove(f)

            plan = [line.strip() for line in plan_lines if not line.startswith(";")]
            log(f"      [SUCCESS] Time: {duration:.4f}s | Nodes: {nodes_expanded} | Branch: {avg_branching:.2f} | Plan Length: {len(plan)}")
            log_csv(algo_name, level_id, "SUCCESS", duration, "Solution Length", len(plan))
            return plan, duration
        else: 
            log("      [FAILED] No plan file generated.")
            log_csv(algo_name, level_id, "FAILED", duration, "Solution Length", 0)
            return None, duration

    except subprocess.TimeoutExpired:
        log(f"      [FAILED] Planner timed out after {time_limit} seconds.")
        log_csv(algo_name, level_id, "TIMEOUT", time_limit, "Plan Length", 0)
        return None, time_limit
    except FileNotFoundError:
        log(f"      [ERROR] Command '{PLANNER_PATH2}' not found.")
        return None, 0

def solve_level(level_str, level_index):
    level_id = f"Level {level_index}"
    log(f"\n=== SOLVING {level_id} ===")
    
    try:
        level = SokobanLevel(level_str)
        log(f"Size: {level.width}x{level.height} | Boxes: {len(level.initial_state.boxes)}")
    except Exception as e:
        log(f"Error parsing level {level_index}: {e}")
        return

    heuristics_to_run = [
        (Manhattan_Distance.heuristic, "Manhattan"),
        (Real_Maze_Distance.heuristic, "Real Maze"),
        (New_Real_Maze_Distance.heuristic, "New Real Maze"),
        (Hungarian_Distance.heuristic, "Hungarian"),
        (Fast_Distance.heuristic, "Fast Distance"),
        (Exact_Distance.heuristic, "Exact Distance"),
        (Satificing.heuristic, "Satisficing"),
    ]

    for h_func, h_name in heuristics_to_run:
        run_astar(level, h_func, h_name, level_id)
    
    pddl_gen = PDDLGenerator(level, level_name=f"level{level_index}")
    problem_filename = f"pddl/problem_{level_index}.pddl"
    
    os.makedirs("pddl", exist_ok=True)
    pddl_gen.write_to_file(problem_filename)
    
    run_fast_downward(DOMAIN_PATH, problem_filename, level_id, time_limit=TIME_LIMIT)
    run_lama_first(DOMAIN_PATH, problem_filename, level_id, time_limit=TIME_LIMIT)

if __name__ == "__main__":
    with open(LOG_FILE, "w") as f:
        f.write("--- EZ LEVEL EXPERIMENT SESSION ---\n")
        f.write(f"Date: {time.ctime()}\n")

    levels = parse_levels(LEVELS_FILE) 
    print(f"Loaded {len(levels)} levels from {LEVELS_FILE}.")

    for i, level_str in enumerate(levels):
        solve_level(level_str, i)