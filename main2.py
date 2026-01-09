import time
import os 
import subprocess
import csv
import re
import signal
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

# --- CONFIGURATION ---
LEVELS_FILE = "sokoban_levels.txt"
PLANNER_PATH = "fast-downward/fast-downward.py" 
PLANNER_PATH2 = "./lama-first"                  
DOMAIN_PATH = "pddl/domain.pddl"
LOG_FILE = "experiment_log.txt"
CSV_FILE = "experiment_data.csv"


ASTAR_LIMIT = 90    
PLANNER_LIMIT =  500

def log(message):
    print(message)
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

def log_csv(algorithm, level_id, status, duration, metric_type, metric_value):
    file_exists = os.path.isfile(CSV_FILE)
    try:
        with open(CSV_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Algorithm", "Level", "Status", "Time (s)", "Metric Type", "Metric Value"])
            writer.writerow([algorithm, level_id, status, f"{duration:.4f}", metric_type, metric_value])
    except Exception as e:
        print(f"Error writing to CSV: {e}")

def parse_levels(filename):
    levels = []
    current_level_lines = []
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return []
        
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith(";") or line.startswith("Title:") or line.startswith("Author:") or line.startswith("Comment:"):
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
    try:
        result = Astar(level.initial_state, get_neighbors, is_goal, h_func, limit=200000, weight=5.0)
    except Exception as e:
        log(f"      [ERROR] A* crashed: {e}")
        return

    end = time.time()
    duration = end - start
    
    path, nodes, mem, branching_stats = result
    avg_b, max_b, min_b = branching_stats
    
    log_csv(algo_name, level_id, "Memory", duration, "Max Stored Nodes", mem)
    log_csv(algo_name, level_id, "Branching", duration, "Avg Branching", avg_b)

    if path:
        log(f"      [SUCCESS] Time: {duration:.4f}s | Nodes: {nodes} | Len: {len(path)}")
        log_csv(algo_name, level_id, "SUCCESS", duration, "Nodes Expanded", nodes)
        log_csv(algo_name, level_id, "SUCCESS", duration, "Solution Length", len(path))
    else:
        log(f"      [FAILED] Time: {duration:.4f}s | Nodes: {nodes}")
        log_csv(algo_name, level_id, "FAILED", duration, "Nodes Expanded", nodes)

def run_fast_downward(domain_file, problem_file, level_id, time_limit):
    algo_name = "Fast Downward"
    log(f"   [Planner] Running {algo_name}...")

    if not os.path.exists(domain_file):
        log(f"      [ERROR] Domain file missing.")
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
        
        # Parse output for metrics
        nodes_expanded = 0
        expanded_matches = re.findall(r"Expanded (\d+) state\(s\)", result.stdout)
        if expanded_matches: nodes_expanded = sum(int(x) for x in expanded_matches)

        log_csv(algo_name, level_id, "Metrics", duration, "Nodes Expanded", nodes_expanded)
        
        if os.path.exists("sas_plan"):
            with open("sas_plan", "r") as f:
                plan_lines = f.readlines()
            plan = [line.strip() for line in plan_lines if not line.startswith(";")]
            os.remove("sas_plan") 
            
            log(f"      [SUCCESS] Time: {duration:.4f}s | Plan Len: {len(plan)}")
            log_csv(algo_name, level_id, "SUCCESS", duration, "Solution Length", len(plan))
        else:
            log(f"      [FAILED] No plan found.")
            log_csv(algo_name, level_id, "FAILED", duration, "Solution Length", 0)

    except Exception as e:
        log(f"      [ERROR] Planner failed: {e}")

def run_lama_first(domain_file, problem_file, level_id, time_limit):
    algo_name = "LAMA First"
    log(f"   [Planner] Running {algo_name}...")

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
        expanded_matches = re.findall(r"Expanded (\d+) state\(s\)", result.stdout)
        if expanded_matches: nodes_expanded = sum(int(x) for x in expanded_matches)

        log_csv(algo_name, level_id, "Metrics", duration, "Nodes Expanded", nodes_expanded)
        
        plan_files = [f for f in os.listdir('.') if f.startswith('sas_plan') and not f.endswith('.pddl')]
        
        if plan_files:
            plan_files.sort()
            best_plan_file = plan_files[-1]
            with open(best_plan_file, "r") as f:
                plan_lines = f.readlines()
            for f in plan_files: os.remove(f)

            plan = [line.strip() for line in plan_lines if not line.startswith(";")]
            log(f"      [SUCCESS] Time: {duration:.4f}s | Plan Len: {len(plan)}")
            log_csv(algo_name, level_id, "SUCCESS", duration, "Solution Length", len(plan))
        else: 
            log("      [FAILED] No plan file generated.")
            log_csv(algo_name, level_id, "FAILED", duration, "Solution Length", 0)

    except subprocess.TimeoutExpired:
        log(f"      [FAILED] Timeout ({time_limit}s).")
        log_csv(algo_name, level_id, "TIMEOUT", time_limit, "Plan Length", 0)
    except Exception as e:
        log(f"      [ERROR] LAMA failed: {e}")

def solve_level(level_str, level_index):
    level_id = f"Level {level_index}"
    log(f"\n=== SOLVING {level_id} ===")
    
    try:
        level = SokobanLevel(level_str)
    except Exception as e:
        log(f"Error parsing level {level_index}: {e}")
        return

    heuristics = [
        (Manhattan_Distance.heuristic, "Manhattan"),
        (Real_Maze_Distance.heuristic, "Real Maze"),
        (New_Real_Maze_Distance.heuristic, "New Real Maze"),
        (Hungarian_Distance.heuristic, "Hungarian"),
        (Fast_Distance.heuristic, "Fast Distance"),
        (Exact_Distance.heuristic, "Exact Distance"),
        (Satificing.heuristic, "Satisficing"),
    ]

    for h_func, h_name in heuristics:
        run_astar(level, h_func, h_name, level_id)
    
    pddl_gen = PDDLGenerator(level, level_name=f"level{level_index}")
    problem_filename = f"pddl/problem_{level_index}.pddl"
    os.makedirs("pddl", exist_ok=True)
    pddl_gen.write_to_file(problem_filename)
    
    run_fast_downward(DOMAIN_PATH, problem_filename, level_id, PLANNER_LIMIT)
    run_lama_first(DOMAIN_PATH, problem_filename, level_id, PLANNER_LIMIT)

if __name__ == "__main__":
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE) 

    with open(LOG_FILE, "w") as f:
        f.write(f"--- FULL EXPERIMENT SESSION: {time.ctime()} ---\n")

    levels = parse_levels(LEVELS_FILE) 
    print(f"Loaded {len(levels)} levels.")

    subset_levels = levels[:5]
    print(f"Running on first {len(subset_levels)} levels only.")

    for i, level_str in enumerate(subset_levels):
        solve_level(level_str, i + 1)