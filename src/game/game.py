# import random
import time
import copy
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from ..environment.world_load import WorldLoader
from ..agent.agent import Agent, AgentConfig
from ..interface.graphical_control import WumpusGraphics
from ..utils.constants import percepts

class WumpusGame:

    def __init__(self, 
                 world_file: str = "worlds/default.world", 
                 agent: Agent = None,
                 graphics: bool = True):
        # Initialize game components
        self.world_loader = WorldLoader(world_file)
        self.original_world = copy.deepcopy(self.world_loader.get_board())
        print(self.original_world) # debugging log
        self.game_world = copy.deepcopy(self.original_world)
        print(self.game_world) # debugging log
        self.world_size = self.world_loader.world_size
        print()
        # Initialize agent
        self.agent = agent if agent else Agent(AgentConfig())
        print(self.agent.__dict__) # debugging log
        
        # Initialize graphics
        self.graphics_enabled = graphics
        if self.graphics_enabled:
            self.graphics = WumpusGraphics()
        else:
            self.graphics = None
        
        # Game state
        self.game_over = False
        self.won = False
        self.step_count = 0
        
        # Initial setup
        self._place_agent_on_board()
        self._update_display("Game initialized")

    def _place_agent_on_board(self) -> None:
        """Place agent on the board at starting position"""
        row, col = self.agent.position
        self.game_world[row][col] = self.agent.agent_config.agent_symbol

    def _update_display(self, status: str) -> None:
        """Update visual display if graphics enabled"""
        if self.graphics_enabled:
            display_board = self.get_display_board()
            self.graphics.draw_board(display_board, self.agent, status)
        else:
            self._print_text_status(status)

    def _print_text_status(self, status: str) -> None:
        """Print text-based status update"""
        print(f"\nStep {self.step_count}: {status}")
        
        # Use display board for text output too
        display_board = self.get_display_board()
        print("  " + " ".join(str(i) for i in range(self.world_size[1])))
        for i, row in enumerate(display_board):
            print(f"{i} " + " ".join(row))
        
        agent_status = self.agent.get_status()
        print(f"\nPosition: {agent_status['position']}")
        print(f"Arrows: {agent_status['arrow_count']}")
        print(f"Gold: {'Yes' if agent_status['has_gold'] else 'No'}")
        print(f"Score: {agent_status['score']}")
        print(f"Percepts: {self.get_percepts()}")

    def get_percepts(self) -> str:      # needs to be monitored
        """Get current percepts based on agent's position"""
        global percepts
        # if self.game_over:
        #     return "Game over"
        row, col = self.agent.position
        if percepts[row][col] != "":
            return percepts[row][col]
        
        percepts[row][col] += "V"
        self.agent.path.append((row, col))  # Track path # newly added
        self.game_world[row][col] = self.agent.agent_config.trail_symbol # Mark as visited 

        adjacent = [(row-1,col), (row+1,col), (row,col-1), (row,col+1)]
        for r, c in adjacent:
            if 0 <= r < self.world_size[0] and 0 <= c < self.world_size[1]:
                cell = self.original_world[r][c]
                if cell == 'W' and "S" not in percepts:
                    percepts.append("S")
                elif cell == 'P' and "B" not in percepts:
                    percepts.append("B")

        if self.original_world[row][col] == 'G':
            percepts[row][col] += "G"
        else:
            percepts[row][col] += "~G"
            
        # if no hazards in current cell
        if 'W' not in self.original_world[row][col]:
            percepts[row][col] += '~W'
        if 'P' not in self.original_world[row][col]:
            percepts[row][col] += '~P'

        print(f"[PERCEPTS] At {self.agent.position} → {percepts[row][col]}") # debugging log
        return percepts[row][col]

    # def get_world_info(self) -> Dict:
    #     """Return complete world information"""
    #     return {
    #         'wumpus_positions': self._find_elements('W'),
    #         'pit_positions': self._find_elements('P'),
    #         'gold_positions': self._find_elements('G'),
    #         'world_size': self.world_size,
    #         'agent_position': self.agent.position
    #     }

    def _find_elements(self, element: str) -> List[Tuple[int, int]]:
        """Find all positions of a specific element"""
        positions = []
        for i, row in enumerate(self.original_world):
            for j, val in enumerate(row):
                if val == element:
                    positions.append((i, j))
        return positions
        
        # Current cell
        if self.original_world[row][col] == 'G':
            percepts.append("Glitter")
            
        return percepts if percepts else ["Nothing"]

    def execute_action(self, action: str, direction: str = None) -> Tuple[bool, str]:
        """Execute a game action and return (success, message)"""
        if self.game_over:
            return False, "Game over"
            
        self.step_count += 1
        
        if action == 'move':
            return self._move_agent(direction)
        elif action == 'shoot':
            return self._shoot_arrow(direction)
        elif action == 'grab':
            return self._grab_gold()
        else:
            return False, f"Unknown action: {action}"

    def _update_board_state(self) -> None:
        """Update the game board representation"""
        self.game_world = copy.deepcopy(self.original_world)
        
        # Mark visited cells
        # for row, col in self.agent.visited_cells:
        #     if (row, col) != self.agent.position:
        #         self.game_world[row][col] = self.agent.agent_config.trail_symbol
        
        # Place agent
        row, col = self.agent.position
        self.game_world[row][col] = self.agent.agent_config.agent_symbol
        
        # Update display
        self._update_display(f"Step {self.step_count}")

    def _handle_death(self, message: str) -> None:
        """Handle death scenario"""
        self.agent.die()
        self.game_over = True
        if self.graphics_enabled:
            self.graphics.animate_death()
        self._update_display(message)

    def _handle_victory(self) -> None:
        """Handle victory scenario"""
        self.won = True
        self.game_over = True
        if self.graphics_enabled:
            self.graphics.animate_victory()
        self._update_display("Victory!")

    def get_game_status(self) -> Dict: # formerly get_game_state
        """Return complete game state"""
        agent_state = self.agent.get_status()
        return {
            **agent_state,
            'world_size': self.world_size,
            'percepts': self.get_percepts(),
            'game_over': self.game_over,
            'won': self.won,
            'step_count': self.step_count,
            'wumpus_alive': 'W' in {cell for row in self.original_world for cell in row}
        }

    def _reset_game(self) -> None:
        """Reset game to initial state"""
        self.original_world = copy.deepcopy(self.world_loader.get_board())
        self.game_world = copy.deepcopy(self.original_world)
        self.agent.reset()
        self.game_over = False
        self.won = False
        self.step_count = 0
        self._place_agent_on_board()
        self._update_display("Game reset")

    def get_display_board(self) -> List[List[str]]:
        """Create a display board that shows breeze and stench indicators"""
        display_board = [row[:] for row in self.game_world]  # Copy game board
        
        # Add breeze indicators where agent would sense nearby pits
        for row in range(self.world_size[0]):
            for col in range(self.world_size[1]):
                # Skip if cell already has something important
                if display_board[row][col] in ['A', 'W', 'P', 'G']:
                    continue
                
                # Check for adjacent hazards
                has_adjacent_pit = False
                has_adjacent_wumpus = False
                
                # Check all adjacent cells
                adjacent = [(row-1,col), (row+1,col), (row,col-1), (row,col+1)]
                for r, c in adjacent:
                    if 0 <= r < self.world_size[0] and 0 <= c < self.world_size[1]:
                        cell = self.original_world[r][c]
                        if cell == 'P':
                            has_adjacent_pit = True
                        elif cell == 'W':
                            has_adjacent_wumpus = True
                
                # Add percept indicators (prioritize stench over breeze if both)
                if has_adjacent_wumpus:
                    display_board[row][col] = 'S'  # Stench
                elif has_adjacent_pit:
                    display_board[row][col] = 'B'  # Breeze
        
        return display_board
    
    
    
    
    
# elite methods that causes the problem. 

    def _move_agent(self, direction: str) -> Tuple[bool, str]:
        """Move agent in specified direction"""
        new_pos = self.agent.get_next_position(direction)
        if not new_pos:
            return False, "Invalid direction"
            
        # # Check boundaries
        # if not (0 <= new_pos[0] < self.world_size[0] and 
        #         0 <= new_pos[1] < self.world_size[1]):
        #     return False, "Cannot move outside world"
        
        # Move agent
        self.agent.move(new_pos)
        row, col = new_pos
        cell_content = self.original_world[row][col]
        
        # Check for hazards
        if cell_content == 'P':
            self._handle_death("💀 You fell into a pit!")
            return False, "Fell into pit"
        elif cell_content == 'W':
            self._handle_death("💀 You were eaten by the Wumpus!")
            return False, "Eaten by Wumpus"
        
        # Check for win condition
        if self.agent.has_won():
            self._handle_victory()
            return True, "🎉 You won!"
            
        # Update display
        self._update_board_state()
        return True, f"Moved {direction} to {new_pos}"

    def _shoot_arrow(self, direction: str) -> Tuple[bool, str]:
        """Handle arrow shooting"""
        global percepts
        
        if not self.agent.shoot_arrow():
            return False, "No arrows left"
            
        row, col = self.agent.position
        dr, dc = self.agent.directions[direction]
        
        # Arrow trajectory
        path = []
        r, c = row + dr, col + dc
        while 0 <= r < self.world_size[0] and 0 <= c < self.world_size[1]:
            path.append((r, c))
            if self.original_world[r][c] == 'W':
                # updated the stench percepts since wumpus died
                if r-1 >= 0 and 'S' in percepts[r-1][c]:
                    percepts[r-1][c].replace('S', "~S") # since wumpus is killed
                if r+1 < self.world_size[0] and 'S' in percepts[r+1][c]:
                    percepts[r+1][c].replace('S', "~S")
                if c-1 >= 0 and 'S' in percepts[r][c-1]:
                    percepts[r][c-1].replace('S', "~S")
                if c+1 < self.world_size[1] and 'S' in percepts[r][c+1]:
                    percepts[r][c+1].replace('S', "~S")
                    
                self.original_world[r][c] = '-'
                self._update_board_state()
                return True, "🏹 You killed the Wumpus!"
            r += dr
            c += dc
            
        return True, "Arrow missed"

    def _grab_gold(self) -> Tuple[bool, str]:
        """Handle gold collection"""
        row, col = self.agent.position
        if self.original_world[row][col] == 'G':
            if self.agent.grab_gold():
                self.original_world[row][col] = '-'
                self._update_board_state()
                return True, "✨ Gold collected!"
            return False, "Already has gold"
        return False, "No gold here"
    
    def run_autonomous(self) -> None:  # main method of this file.
        """Run game in autonomous mode with AI agent"""
        while not self.game_over:
            percepts = self.get_percepts()
            action, reason = self.agent.decide_action(percepts)
            
            if action == 'move':
                success, message = self._move_agent(reason)
            elif action == 'shoot':
                success, message = self._shoot_arrow(reason)
            elif action == 'grab':
                success, message = self._grab_gold()
            else:
                # time.sleep(0.5)
                continue
                
            print(f"Action: {action} {reason} - {message}")
            # time.sleep(0.5)