from collections import deque

class SokobanState:
    def __init__(self, player, boxes):
        self.player = player
        self.boxes = boxes

    def __hash__(self):
        return hash((self.player, self.boxes))

    def __eq__(self, other):
        return self.player == other.player and self.boxes == other.boxes
    
    def __lt__(self, other):
        return hash(self) < hash(other)

class SokobanLevel:
    def __init__(self, level_string):
        self.walls = set()
        self.goals = set()
        self.width = 0
        self.height = 0
    
        start_player = None
        start_boxes = set()

        lines = level_string.strip().split('\n')
        self.height = len(lines)
        self.width = max(len(line) for line in lines)

        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char == '#':
                    self.walls.add((x, y))
                elif char == '.':
                    self.goals.add((x, y))
                elif char == '$':
                    start_boxes.add((x, y))
                elif char == '*': 
                    start_boxes.add((x, y))
                    self.goals.add((x, y))
                elif char == '@':
                    start_player = (x, y)
                elif char == '+': 
                    start_player = (x, y)
                    self.goals.add((x, y))


        initial_raw_player = start_player
        initial_boxes = frozenset(start_boxes)
        
        reachable = self.get_reachable_simple(initial_raw_player, initial_boxes)
        canonical_player = min(reachable)
        
        self.initial_state = SokobanState(canonical_player, initial_boxes)
        
        self.deadlock_squares = self.find_dead_squares()

    def get_reachable_simple(self, player_pos, boxes):
        queue = deque([player_pos])
        reachable = {player_pos}
        while queue:
            cx, cy = queue.popleft()
            moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            for dx, dy in moves:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) not in self.walls and (nx, ny) not in boxes and (nx, ny) not in reachable:
                    reachable.add((nx, ny))
                    queue.append((nx, ny))
        return reachable

    def find_dead_squares(self):
        safe_squares = set(self.goals)
        queue = deque(self.goals)
        
        moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        while queue:
            box_x, box_y = queue.popleft()
            
            for dx, dy in moves:
                prev_box_x, prev_box_y = box_x - dx, box_y - dy

                player_x, player_y = prev_box_x - dx, prev_box_y - dy
                
                prev_pos = (prev_box_x, prev_box_y)
                player_pos = (player_x, player_y)
                
                if not (0 <= prev_box_x < self.width and 0 <= prev_box_y < self.height):
                    continue
                if not (0 <= player_x < self.width and 0 <= player_y < self.height):
                    continue
                
                if prev_pos not in self.walls and player_pos not in self.walls:
                    if prev_pos not in safe_squares:
                        safe_squares.add(prev_pos)
                        queue.append(prev_pos)
                        
        dead_squares = set()
        for x in range(self.width):
            for y in range(self.height):
                if (x, y) not in self.walls and (x, y) not in safe_squares:
                    dead_squares.add((x, y))
                    
        return dead_squares

    def is_dynamic_deadlock(self, box_pos, boxes):
        x, y = box_pos
        obstacles = self.walls | boxes
        subgrids = [
            [(x, y), (x+1, y), (x, y+1), (x+1, y+1)],
            [(x, y), (x-1, y), (x, y+1), (x-1, y+1)],
            [(x, y), (x+1, y), (x, y-1), (x+1, y-1)],
            [(x, y), (x-1, y), (x, y-1), (x-1, y-1)]
        ]
        
        for grid in subgrids:

            if all(cell in obstacles for cell in grid):
                
                boxes_in_grid = [cell for cell in grid if cell in boxes]
                
                if any(b not in self.goals for b in boxes_in_grid):
                    return True
                    
        return False

    def print_state(self, state):
        output = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                pos = (x, y)
                if pos in self.walls:
                    line.append('#')
                elif pos in state.boxes:
                    line.append('*' if pos in self.goals else '$')
                elif pos in self.goals:
                    line.append('.')
                elif pos == state.player:
                    line.append('@')
                else:
                    line.append(' ')
            output.append("".join(line))
        return "\n".join(output)
    
    def get_reachable(self, player_pos, boxes):
        return self.get_reachable_simple(player_pos, boxes)

    def get_successors(state, level):
        successors = []
        current_reachable = level.get_reachable(state.player, state.boxes)
        
        moves = {
            'U': (0, -1), 'D': (0, 1), 
            'L': (-1, 0), 'R': (1, 0)
        }

        for box in state.boxes:
            bx, by = box
            for move_name, (dx, dy) in moves.items():
                push_from_pos = (bx - dx, by - dy)
                if push_from_pos not in current_reachable:
                    continue
                
                new_box_pos = (bx + dx, by + dy)
                if new_box_pos in level.walls or new_box_pos in state.boxes:
                    continue
                if new_box_pos in level.deadlock_squares:
                    continue
                
                new_boxes = set(state.boxes)
                new_boxes.remove(box)
                new_boxes.add(new_box_pos)
                frozenset_boxes = frozenset(new_boxes)
                
                if level.is_dynamic_deadlock(new_box_pos, frozenset_boxes):
                    continue
                
                raw_player_pos = box 
                new_reachable = level.get_reachable(raw_player_pos, frozenset_boxes)
                canonical_player_pos = min(new_reachable)
                
                new_state = SokobanState(canonical_player_pos, frozenset_boxes)
                successors.append((move_name, new_state))


        return successors

    def is_goal(state, level): return state.boxes.issubset(level.goals)