# Sokoban AI Solver

This repository contains the implementation of an AI-based solver for the Sokoban puzzle game. It was developed as part of the Artificial Intelligence homework.

The project implements an entire pipeline of AI experiments, including:
1.  Problem Modeling: A representation of the Sokoban environment.
2.  Search Algorithms: A custom implementation of A* with various heuristics.
3.  Automated Planning: Modeling the problem in PDDL and solving it using external planners (Fast Downward and LAMA).

# Project Structure

* 'main.py': The entry point for running experiments. It loads the original levels, runs A*, generates PDDL files, and invokes external planners.
* 'main_ez.py':  The entrypoint for running the easier levels.
* 'Sokoban.py': Contains the 'SokobanLevel' class and game logic.
* 'Astar.py': A generic, modular implementation of the A* search algorithm.
* 'heuristics/': Contains different heuristic implementations for A*.
* 'pddl/': Directory where PDDL domain and problem files are generated.
* 'fast-downward/': Contains the Fast Downward planner.
* 'sokoban_levels.txt': The original sokoban levels
* 'ez_levels.txt': The AI generated easier levels


# Python Libraries
The project requires Python 3.

You can install the necessary Python dependencies using pip:

Install the required dependencies using pip:
'''bash
pip install -r requirements.txt


# External Planners

To fulfill the requirement of using an AI technique different from A*, this project interfaces with PDDL planners.

* Fast Downward:
This planner is included in the repository within the fast-downward/ directory.

* LAMA (LAMA-First):
Handled via Wrapper: The repository includes a lama-first script in the root directory.

This script uses planutils to chek if LAMA is installed. If it is missing, the script will prompt you to download and install it automatically during the first run.

Note: Ensure planutils is installed (this is handled via the requirements.txt installation).


# How to Run

Configure the Level: Ensure a level file (e.g., ez_level.txt) is present in the root directory. You can change the target file by modifying the LEVELS_FILE variable in the main.py's (plural).

Run the main script from the terminal:

python main.py
python main_ez.py


Output:
Console: Displays real-time progress for A* and the planners.
Logs: Detailed execution logs are saved to experiment_log.txt/experiment_log_ez.txt. (depends on wich main)
Data: Metrics such as execution time, nodes expanded, and memory usage are exported to experiment_data.csv/experiment_data_ez.csv.