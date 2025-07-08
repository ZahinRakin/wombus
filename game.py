from world_load import WorldLoader
from agent import Agent, AgentConfig
from graphical_control import wompus_graphics
import copy


class WumpusGame:
    
    def __init__(self, world_file='world.txt', agent: Agent = Agent(AgentConfig())):
        # Load world
        self.graphics = wompus_graphics()
        self.world_loader = WorldLoader(world_file)
        loaded_board = self.world_loader.get_board()
        if not loaded_board:
            raise ValueError("Failed to load world!")
        
        self.original_world = copy.deepcopy(loaded_board)
        self.game_world = copy.deepcopy(loaded_board)
        self.world_size = self.world_loader.world_size
        
        # Setup agent
        self.agent = agent
        
        # Game state
        self.game_over = False
        self.won = False
        
        # Place agent on board
        self._place_agent_on_board()
    
    def _place_agent_on_board(self):
        row, col = self.agent.get_position()
        self.game_world[row][col] = self.agent.agent_config.agent_symbol
    
    def _update_board_display(self):
        # Reset board to original state
        self.game_world = copy.deepcopy(self.original_world)
        
        # Mark visited cells
        for row, col in self.agent.visited_cells:
            if (row, col) != self.agent.get_position():
                if self.original_world[row][col] == '-':
                    self.game_world[row][col] = self.agent.agent_config.trail_symbol
        
        # Place agent
        row, col = self.agent.get_position()
        self.game_world[row][col] = self.agent.agent_config.agent_symbol
        
        # graphics
        self.graphics.draw_board(self.game_world)
    
    def print_board(self):
        """Print the current game board"""
        # graphics
        self.graphics.draw_board(self.game_world)
        # printing on terminal
        self._update_board_display()
        print("\nCurrent Game State:")
        print("  " + " ".join([str(i) for i in range(self.world_size[1])]))
        for i in range(self.world_size[0]):
            print(f"{i} ", end="")
            for j in range(self.world_size[1]):
                print(self.game_world[i][j], end=' ')
            print()
    
    def get_percepts(self):
        """Get percepts at agent's current position"""
        percepts = []
        row, col = self.agent.get_position()
        
        if self._check_adjacent_danger('P'):
            percepts.append("Breeze")
        
        if self._check_adjacent_danger('W'):
            percepts.append("Stench")
        
        if self.original_world[row][col] == 'G':
            percepts.append("Glitter")
        
        return percepts if percepts else ["Nothing"]
    
    def _check_adjacent_danger(self, danger_type):
        row, col = self.agent.get_position()
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < self.world_size[0] and 0 <= new_col < self.world_size[1] and 
                self.original_world[new_row][new_col] == danger_type):
                return True
        return False
    
    def is_valid_position(self, position):
        row, col = position
        return 0 <= row < self.world_size[0] and 0 <= col < self.world_size[1]
    
    def move_agent(self, direction):
        if self.game_over:
            return False, "Game is over!"
        
        new_position = self.agent.get_next_position(direction)
        if not new_position:
            return False, "Invalid direction!"
        
        if not self.is_valid_position(new_position):
            return False, "Cannot move outside the board!"
        
        self.agent.move(direction)
        
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
        
        if self.agent.has_won():
            self.won = True
            self.game_over = True
            return True, "🎉 Congratulations! You won the game!"
        
        return True, "Move successful"
    
    def grab_gold(self):
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
        if self.game_over:
            return False, "Game is over!"
        
        if not self.agent.shoot_arrow():
            return False, "You don't have an arrow!"
        
        row, col = self.agent.get_position()
        dr, dc = self.agent.directions.get(direction, (0, 0))
        
        current_row, current_col = row + dr, col + dc
        while self.is_valid_position((current_row, current_col)):
            if self.original_world[current_row][current_col] == 'W':
                self.original_world[current_row][current_col] = '-'
                return True, "🏹 You killed the Wumpus!"
            current_row += dr
            current_col += dc
        
        return True, "Arrow missed!"
    
    def get_game_status(self):
        agent_status = self.agent.get_status()
        return {
            **agent_status,
            'percepts': self.get_percepts(),
            'game_over': self.game_over,
            'won': self.won
        }
    
    def print_status(self):
        status = self.get_game_status()
        print(f"\nAgent Position: {status['position']}")
        print(f"Arrow Count: {status['arrow_count']}")
        print(f"Has Gold: {status['has_gold']}")
        print(f"Score: {status['score']}")
        print(f"Percepts: {status['percepts']}")
        print(f"Visited Cells: {status['visited_cells']}")
    
    def reset_game(self):
        self.original_world = copy.deepcopy(self.world_loader.get_board())
        self.game_world = copy.deepcopy(self.original_world)
        self.agent.reset()
        self.game_over = False
        self.won = False
        self._place_agent_on_board()
    
    def get_world_info(self):
        return {
            'wumpus_positions': self.world_loader.find_elements('W'),
            'pit_positions': self.world_loader.find_elements('P'),
            'gold_positions': self.world_loader.find_elements('G'),
            'world_size': (self.world_size[0], self.world_size[1])
        }


# For testing purposes
def test_all_game_methods():
    try:
        game = WumpusGame()
        print("\n✅ Game initialized successfully.")
        
        # Print initial world info
        print("\n🌍 World info:")
        print(game.get_world_info())
        
        # Print initial board and status
        print("\n📋 Initial Board:")
        game.print_board()
        game.print_status()
        
        # Test moving in all directions
        for direction in ['up', 'down', 'left', 'right']:
            success, msg = game.move_agent(direction)
            print(f"\n➡️ Move {direction}: {success}, {msg}")
            game.print_board()
            game.print_status()
            if game.game_over:
                print("💥 Game ended due to hazard.")
                break
        
        # Try grabbing gold
        print("\n🪙 Try grabbing gold:")
        success, msg = game.grab_gold()
        print(f"Grab gold: {success}, {msg}")
        
        # Try shooting arrow in all directions
        for direction in ['up', 'down', 'left', 'right']:
            success, msg = game.shoot_arrow(direction)
            print(f"\n🏹 Shoot {direction}: {success}, {msg}")
            if not success:
                break  # No more arrows
        
        # Print final status
        print("\n📊 Final Status:")
        game.print_status()
        
        # Reset game
        print("\n🔄 Resetting game...")
        game.reset_game()
        game.print_board()
        game.print_status()
    
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")


if __name__ == "__main__":
    test_all_game_methods()

