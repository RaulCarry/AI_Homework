class PDDLGenerator:
    def __init__(self, level, level_name="sokoban_problem"):
        self.level = level
        self.name = level_name
        self.width = level.width
        self.height = level.height
        self.walls = level.walls
        self.initial_state = level.initial_state
        self.goals = level.goals

    def generate_problem_pddl(self):

        pddl = f"(define (problem {self.name})\n"
        pddl += "  (:domain sokoban)\n"

        objects = "  (:objects\n    "
        objects += "up down left right - direction\n    "

        locations = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.walls:
                    locations.append(f"pos_{x}_{y}")
        
        objects += " ".join(locations) + " - location\n"
        objects += "  )\n"
        pddl += objects

        pddl += "  (:init\n"
        
        directions = {
            'up': (0, -1),
            'down': (0, 1),
            'left': (-1, 0),
            'right': (1, 0)
        }
        
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.walls:
                    continue
                
                curr_str = f"pos_{x}_{y}"
                
                for d_name, (dx, dy) in directions.items():
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self.width and 0 <= ny < self.height) and (nx, ny) not in self.walls:
                        next_str = f"pos_{nx}_{ny}"
                        pddl += f"    (move-dir {curr_str} {next_str} {d_name})\n"

        px, py = self.initial_state.player
        pddl += f"    (at-player pos_{px}_{py})\n"
        
        box_positions = set(self.initial_state.boxes)
        for (bx, by) in box_positions:
            pddl += f"    (at-box pos_{bx}_{by})\n"

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.walls:
                    continue
                if (x, y) == (px, py):
                    continue
                if (x, y) in box_positions:
                    continue
                pddl += f"    (clear pos_{x}_{y})\n"
                
        pddl += "  )\n"

        pddl += "  (:goal (and\n"
        for (gx, gy) in self.goals:
            pddl += f"    (at-box pos_{gx}_{gy})\n"
        pddl += "  ))\n"
        
        pddl += ")"
        return pddl

    def write_to_file(self, filename):
        content = self.generate_problem_pddl()
        with open(filename, "w") as f:
            f.write(content)
        return filename