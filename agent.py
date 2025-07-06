class Agent:
    
    def __init__(self, starting_position=(9, 0)):
        self.position = starting_position
        self.starting_position = starting_position
        self.visited_cells = set()
        self.visited_cells.add(starting_position)
        
        # Inventory and capabilities
        self.has_arrow = True
        self.has_gold = False
        
        # Game state
        self.is_alive = True
        self.score = 0
        
        # Directions mapping
        self.directions = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }
    
    def get_position(self):
        return self.position
    
    def set_position(self, new_position):
        self.position = new_position
        self.visited_cells.add(new_position)
    
    def get_next_position(self, direction):
        if direction not in self.directions:
            return None
        
        dr, dc = self.directions[direction]
        row, col = self.position
        if (0 <= row + dr < 10 and 0 <= col + dc < 10):
            return (row + dr, col + dc)
        else:
            print("Invalid move: Out of the world!!")
            return (row, col)
    
    def move(self, direction):
        new_position = self.get_next_position(direction)
        if new_position:
            self.set_position(new_position)
            self.score -= 1  # Movement cost
            return new_position
        return None
    
    def grab_gold(self):
        if not self.has_gold:
            self.has_gold = True
            self.score += 1000
            return True
        return False
    
    def shoot_arrow(self):
        if self.has_arrow:
            self.has_arrow = False
            self.score -= 10  # Arrow cost
            return True
        return False
    
    def die(self):
        self.is_alive = False
        self.score -= 1000
    
    def is_at_starting_position(self):
        return self.position == self.starting_position
    
    def has_won(self):
        return self.has_gold and self.is_at_starting_position()
    
    def get_status(self):
        return {
            'position': self.position,
            'has_arrow': self.has_arrow,
            'has_gold': self.has_gold,
            'is_alive': self.is_alive,
            'score': self.score,
            'visited_cells': len(self.visited_cells)
        }
    
    def reset(self):
        self.position = self.starting_position
        self.visited_cells = set()
        self.visited_cells.add(self.starting_position)
        self.has_arrow = True
        self.has_gold = False
        self.is_alive = True
        self.score = 0
