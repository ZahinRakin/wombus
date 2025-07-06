from world_load import WorldLoader
from agent import Agent, AgentConfig


class WumpusGame:
    
    def __init__(self, world_file='world.txt', agent_config=None):
        # Load world
        self.world_loader = WorldLoader(world_file)
        if not self.world_loader.get_board():
            raise ValueError("Failed to load world!")
        
        # Setup agent
        if agent_config is None:
            agent_config = AgentConfig()
        self.agent_config = agent_config
        self.agent = Agent(agent_config.starting_position)
        
        # Game state
        self.original_world = self.world_loader.get_board()
        self.game_world = self.world_loader.get_board()  # Copy for game state
        self.world_size = len(self.original_world)
        self.game_over = False
        self.won = False
        
        # Place agent on board
        self._place_agent_on_board()
    
    def _place_agent_on_board(self):
        row, col = self.agent.get_position()
        self.game_world[row][col] = self.agent_config.agent_symbol
    
    def _update_board_display(self):
        # Reset board to original state
        self.game_world = self.world_loader.get_board()
        
        # Mark visited cells
        for row, col in self.agent.visited_cells:
            if (row, col) != self.agent.get_position():
                if self.original_world[row][col] == '-':
                    self.game_world[row][col] = self.agent_config.trail_symbol
        
        # Place agent
        row, col = self.agent.get_position()
        self.game_world[row][col] = self.agent_config.agent_symbol
    
    def print_board(self):
        """Print the current game board"""
        self._update_board_display()
        print("\nCurrent Game State:")
        print("  " + " ".join([str(i) for i in range(self.world_size)]))
        for i in range(self.world_size):
            print(f"{i} ", end="")
            for j in range(self.world_size):
                print(self.game_world[i][j], end=' ')
            print()
    
    def get_percepts(self):
        """Get percepts at agent's current position"""
        percepts = []
        row, col = self.agent.get_position()
        
        # Check for breeze (adjacent pit)
        if self._check_adjacent_danger('P'):
            percepts.append("Breeze")
        
        # Check for stench (adjacent wumpus)
        if self._check_adjacent_danger('W'):
            percepts.append("Stench")
        
        # Check for glitter (gold at current position)
        if self.original_world[row][col] == 'G':
            percepts.append("Glitter")
        
        return percepts if percepts else ["Nothing"]
    
    def _check_adjacent_danger(self, danger_type):
        """Check if danger (pit or wumpus) is in adjacent cells"""
        row, col = self.agent.get_position()
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < self.world_size and 0 <= new_col < self.world_size and 
                self.original_world[new_row][new_col] == danger_type):
                return True
        return False
    
    def is_valid_position(self, position):
        """Check if position is within board boundaries"""
        row, col = position
        return 0 <= row < self.world_size and 0 <= col < self.world_size
    
    def move_agent(self, direction):
        """Move agent in specified direction"""
        if self.game_over:
            return False, "Game is over!"
        
        new_position = self.agent.get_next_position(direction)
        if not new_position:
            return False, "Invalid direction!"
        
        if not self.is_valid_position(new_position):
            return False, "Cannot move outside the board!"
        
        # Move agent
        self.agent.move(direction)
        
        # Check what's at the new position
        row, col = new_position
        cell_content = self.original_world[row][col]
        
        if cell_content == 'P':
            self.agent.die()
            self.game_over = True
            return False, "💀 You fell into a pit! Game Over!"
        elif cell_content == 'W':
            self.agent.die()
            self.game_over = True
            return False, "💀 You were eaten by the Wumpus! Game Over!"
        
        # Check win condition
        if self.agent.has_won():
            self.won = True
            self.game_over = True
            return True, "🎉 Congratulations! You won the game!"
        
        return True, "Move successful"
    
    def grab_gold(self):
        """Agent attempts to grab gold"""
        if self.game_over:
            return False, "Game is over!"
        
        row, col = self.agent.get_position()
        if self.original_world[row][col] == 'G':
            if self.agent.grab_gold():
                return True, "✨ You grabbed the gold!"
            else:
                return False, "You already have the gold!"
        else:
            return False, "No gold here!"
    
    def shoot_arrow(self, direction):
        """Agent shoots arrow in specified direction"""
        if self.game_over:
            return False, "Game is over!"
        
        if not self.agent.has_arrow:
            return False, "You don't have an arrow!"
        
        # Shoot arrow
        self.agent.shoot_arrow()
        
        # Check if arrow hits wumpus
        row, col = self.agent.get_position()
        dr, dc = self.agent.directions.get(direction, (0, 0))
        
        # Trace arrow path
        current_row, current_col = row + dr, col + dc
        while self.is_valid_position((current_row, current_col)):
            if self.original_world[current_row][current_col] == 'W':
                # Kill the wumpus
                self.original_world[current_row][current_col] = '-'
                return True, "🏹 You killed the Wumpus!"
            current_row += dr
            current_col += dc
        
        return True, "Arrow missed!"
    
    def get_game_status(self):
        """Get comprehensive game status"""
        agent_status = self.agent.get_status()
        return {
            **agent_status,
            'percepts': self.get_percepts(),
            'game_over': self.game_over,
            'won': self.won
        }
    
    def print_status(self):
        """Print current game status"""
        status = self.get_game_status()
        print(f"\nAgent Position: {status['position']}")
        print(f"Has Arrow: {status['has_arrow']}")
        print(f"Has Gold: {status['has_gold']}")
        print(f"Score: {status['score']}")
        print(f"Percepts: {status['percepts']}")
        print(f"Visited Cells: {status['visited_cells']}")
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.original_world = self.world_loader.get_board()
        self.game_world = self.world_loader.get_board()
        self.agent.reset()
        self.game_over = False
        self.won = False
        self._place_agent_on_board()
    
    def get_world_info(self):
        """Get information about the world layout"""
        return {
            'wumpus_positions': self.world_loader.find_elements('W'),
            'pit_positions': self.world_loader.find_elements('P'),
            'gold_positions': self.world_loader.find_elements('G'),
            'world_size': (self.world_size, self.world_size)
        }


# For testing purposes
if __name__ == "__main__":
    try:
        game = WumpusGame()
        print("Game initialized successfully!")
        print(f"World info: {game.get_world_info()}")
        
        game.print_board()
        game.print_status()
        
        # Test a move
        success, message = game.move_agent('up')
        print(f"\nMove result: {success}, {message}")
        game.print_status()
        
    except Exception as e:
        print(f"Error initializing game: {e}")
