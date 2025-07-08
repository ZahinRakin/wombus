
class AgentConfig:
    
    def __init__(self, starting_position: tuple = (9,0), 
                    movement_cost: int = 1, 
                    arrow_count: int = 2, 
                    arrow_cost: int = 10, 
                    gold_reward: int = 1000, 
                    death_penalty: int = 1000, 
                    win_bonus: int = 0, 
                    agent_symbol: str = 'A', 
                    trail_symbol: str='.'):
        # Default configuration
        self.starting_position = starting_position
        self.movement_cost = movement_cost
        self.arrow_count = arrow_count
        self.arrow_cost = arrow_cost  # this has fixed in the logic before. have to make that dynamic
        self.gold_reward = gold_reward
        self.death_penalty = death_penalty
        self.win_bonus = win_bonus
        
        # Visual settings
        self.agent_symbol = agent_symbol
        self.trail_symbol = trail_symbol
        
    def get_config(self):
        return {
            'starting_position': self.starting_position,
            'movement_cost': self.movement_cost,
            'arrow_cost': self.arrow_cost,
            'arrow_count': self.arrow_count,
            'gold_reward': self.gold_reward,
            'death_penalty': self.death_penalty,
            'win_bonus': self.win_bonus,
            'agent_symbol': self.agent_symbol,
            'trail_symbol': self.trail_symbol
        }




class Agent:
    
    def __init__(self, agent_config: AgentConfig):
        self.agent_config = agent_config
        self.position = agent_config.starting_position
        self.starting_position = agent_config.starting_position
        self.visited_cells = set()
        self.visited_cells.add(agent_config.starting_position)
        
        # Inventory and capabilities
        self.arrow_count = agent_config.arrow_count
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
        
        dr, dc = self.directions[direction] # dr = delta_row and dc = delta_column
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
            self.score += self.agent_config.gold_reward
            return True
        return False
    
    def shoot_arrow(self):
        if self.arrow_count > 0:
            self.arrow_count -= 1
            self.score -= self.agent_config.arrow_cost
            return True
        return False
    
    def die(self):
        self.is_alive = False
        self.score -= self.agent_config.death_penalty
    
    def is_at_starting_position(self):
        return self.position == self.agent_config.starting_position
    
    def has_won(self):
        return self.has_gold and self.is_at_starting_position()
    
    def get_status(self):
        return {
            'position': self.position,
            'arrow_count': self.arrow_count,
            'has_gold': self.has_gold,
            'is_alive': self.is_alive,
            'score': self.score,
            'visited_cells': len(self.visited_cells)
        }
    
    def reset(self):
        self.position = self.agent_config.starting_position
        self.visited_cells = set()
        self.visited_cells.add(self.agent_config.starting_position)
        self.arrow_count = self.agent_config.arrow_count
        self.has_gold = False
        self.is_alive = True
        self.score = 0


def create_agent():
    config = AgentConfig(
        starting_position = (9,0), 
        movement_cost= 1, 
        arrow_count= 2, 
        arrow_cost= 10, 
        gold_reward= 1000, 
        death_penalty= 1000, 
        win_bonus= 0, 
        agent_symbol = 'A', 
        trail_symbol='.'
    )
    agent = Agent(config)
    
    print("Agent created:")
    print(f"Status: {agent.get_status()}")
    print(f"Config: {config.get_config()}")
    
    # Test movement
    print(f"\nMoving up from {agent.get_position()}")
    new_pos = agent.move('up')
    print(f"New position: {new_pos}")
    print(f"Status: {agent.get_status()}")


# for checiking is everything ok?
if __name__ == "__main__":
    create_agent()
