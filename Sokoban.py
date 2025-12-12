
class SokobanState:
    
    def __init__(self, player, boxes):
        self.player = player
        self.boxes = boxes

    def __hash__(self):
        return hash((self.player, self.boxes))

    def __eq__(self, other):
        return self.player == other.player and self.boxes == other.boxes

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

        self.initial_state = SokobanState(start_player, frozenset(start_boxes))

    def print_state(self, state):
        output = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                pos = (x, y)
                if pos in self.walls:
                    line.append('#')
                elif pos == state.player:
                    line.append('+' if pos in self.goals else '@')
                elif pos in state.boxes:
                    line.append('*' if pos in self.goals else '$')
                elif pos in self.goals:
                    line.append('.')
                else:
                    line.append(' ')
            output.append("".join(line))
        return "\n".join(output)
    
    
    MOVES = {
        'U': (0, -1),
        'D': (0, 1),
        'L': (-1, 0),
        'R': (1, 0)
        }

    def get_successors(state, level):
        successors = []
        
        player_x, player_y = state.player

        for move_name, (dx, dy) in SokobanLevel.MOVES.items():
            new_x, new_y = player_x + dx, player_y + dy
            new_pos = (new_x, new_y)


            if new_pos in level.walls:
                continue

            if new_pos in state.boxes:
                
                new_box_x, new_box_y = new_x + dx, new_y + dy
                new_box_pos = (new_box_x, new_box_y)

                if new_box_pos in level.walls or new_box_pos in state.boxes:
                    continue
                
                new_boxes = set(state.boxes)
                new_boxes.remove(new_pos)
                new_boxes.add(new_box_pos)
                
                new_state = SokobanState(new_pos, frozenset(new_boxes))
                successors.append((move_name, new_state))

            else:
                new_state = SokobanState(new_pos, state.boxes)
                successors.append((move_name, new_state))

        return successors

    def is_goal(state, level): return state.boxes.issubset(level.goals)
    
    
    
    