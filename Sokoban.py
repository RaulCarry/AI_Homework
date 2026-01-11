import collections
from collections import namedtuple, deque

SokobanState = namedtuple('SokobanState', ['boxes', 'player'])

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

        self.initial_state = SokobanState(initial_boxes, canonical_player)
        
        self.deadlock_squares = self.find_dead_squares()

    def get_reachable_simple(self, player_pos, boxes):
        """BFS to find all reachable cells for the player."""
        queue = deque([player_pos])
        reachable = {player_pos}
        
        walls = self.walls
        
        while queue:
            cx, cy = queue.popleft()
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nx, ny = cx + dx, cy + dy
                if (nx, ny) not in walls and (nx, ny) not in boxes and (nx, ny) not in reachable:
                    reachable.add((nx, ny))
                    queue.append((nx, ny))
        return reachable

    def find_dead_squares(self):
        """
        Identify squares where a box can NEVER reach a goal.
        Uses Reverse BFS (Pulling from goals).
        """
        safe_squares = set(self.goals)
        queue = deque(self.goals)
        walls = self.walls
        width, height = self.width, self.height
        
        moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        while queue:
            bx, by = queue.popleft()
            
            for dx, dy in moves:

                px, py = bx - dx, by - dy
                ppx, ppy = px - dx, py - dy
                
                prev_pos = (px, py)
                
                # Bounds check
                if not (0 <= px < width and 0 <= py < height): continue
                if not (0 <= ppx < width and 0 <= ppy < height): continue
                
                if prev_pos not in walls and (ppx, ppy) not in walls:
                    if prev_pos not in safe_squares:
                        safe_squares.add(prev_pos)
                        queue.append(prev_pos)
                        
        dead_squares = set()
        for x in range(width):
            for y in range(height):
                if (x, y) not in walls and (x, y) not in safe_squares:
                    dead_squares.add((x, y))
        return dead_squares

    def is_dynamic_deadlock(self, bx, by, boxes):
        """
        Optimized check for 2x2 frozen deadlocks.
        """
        walls = self.walls
        goals = self.goals
        
        # Check Down-Right (dx=1, dy=1)
        if (bx+1, by) in walls or (bx+1, by) in boxes:
            if (bx, by+1) in walls or (bx, by+1) in boxes:
                if (bx+1, by+1) in walls or (bx+1, by+1) in boxes:
                    sq = [(bx, by), (bx+1, by), (bx, by+1), (bx+1, by+1)]
                    for c in sq:
                        if c in boxes and c not in goals: return True

        # Check Down-Left (dx=-1, dy=1)
        if (bx-1, by) in walls or (bx-1, by) in boxes:
            if (bx, by+1) in walls or (bx, by+1) in boxes:
                if (bx-1, by+1) in walls or (bx-1, by+1) in boxes:
                    sq = [(bx, by), (bx-1, by), (bx, by+1), (bx-1, by+1)]
                    for c in sq:
                        if c in boxes and c not in goals: return True

        # Check Up-Right (dx=1, dy=-1)
        if (bx+1, by) in walls or (bx+1, by) in boxes:
            if (bx, by-1) in walls or (bx, by-1) in boxes:
                if (bx+1, by-1) in walls or (bx+1, by-1) in boxes:
                    sq = [(bx, by), (bx+1, by), (bx, by-1), (bx+1, by-1)]
                    for c in sq:
                        if c in boxes and c not in goals: return True

        # Check Up-Left (dx=-1, dy=-1)
        if (bx-1, by) in walls or (bx-1, by) in boxes:
            if (bx, by-1) in walls or (bx, by-1) in boxes:
                if (bx-1, by-1) in walls or (bx-1, by-1) in boxes:
                    sq = [(bx, by), (bx-1, by), (bx, by-1), (bx-1, by-1)]
                    for c in sq:
                        if c in boxes and c not in goals: return True
                        
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

    @staticmethod
    def get_successors(state, level):
        successors = []

        boxes, player = state 
        
        current_reachable = level.get_reachable_simple(player, boxes)
        
        moves = (('U', 0, -1), ('D', 0, 1), ('L', -1, 0), ('R', 1, 0))
        walls = level.walls
        deadlock_squares = level.deadlock_squares

        for box in boxes:
            bx, by = box
            for move_name, dx, dy in moves:
                push_x, push_y = bx - dx, by - dy
                if (push_x, push_y) not in current_reachable:
                    continue
                
                new_bx, new_by = bx + dx, by + dy
                new_box_pos = (new_bx, new_by)
                
                if new_box_pos in walls or new_box_pos in boxes:
                    continue
                
                # 1. Static Deadlock
                if new_box_pos in deadlock_squares:
                    continue
                
                new_boxes_set = set(boxes)
                new_boxes_set.remove(box)
                new_boxes_set.add(new_box_pos)
                new_boxes = frozenset(new_boxes_set)
                
                # 2. Dynamic Deadlock
                if level.is_dynamic_deadlock(new_bx, new_by, new_boxes):
                    continue
                
                new_reachable = level.get_reachable_simple(box, new_boxes)
                canonical_player = min(new_reachable)
                
                successors.append((move_name, SokobanState(new_boxes, canonical_player)))

        return successors

    @staticmethod
    def is_goal(state, level): 
        return state.boxes.issubset(level.goals)