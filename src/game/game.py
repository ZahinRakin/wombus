# import random
import time
import copy
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from ..environment.world_load import WorldLoader
from ..agent.agent import Agent, AgentConfig
from ..interface.graphical_control import WumpusGraphics

class WumpusGame:
    def __init__(self, 
                 world_file: str = "worlds/default.world", 
                 agent: Agent = None,
                 graphics: bool = True):
        # Initialize game components
        self.world_loader = WorldLoader(world_file)
        self.original_world = copy.deepcopy(self.world_loader.get_board())
        self.game_world = copy.deepcopy(self.original_world)
        self.world_size = self.world_loader.world_size
        
        # Initialize agent
        self.agent = agent if agent else Agent(AgentConfig())
        
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
            self.graphics.draw_board(self.game_world, self.agent, status)
        else:
            self._print_text_status(status)

    def _print_text_status(self, status: str) -> None:
        """Print text-based status update"""
        print(f"\nStep {self.step_count}: {status}")
        print("  " + " ".join(str(i) for i in range(self.world_size[1])))
        for i, row in enumerate(self.game_world):
            print(f"{i} " + " ".join(row))
        
        agent_status = self.agent.get_status()
        print(f"\nPosition: {agent_status['position']}")
        print(f"Arrows: {agent_status['arrow_count']}")
        print(f"Gold: {'Yes' if agent_status['has_gold'] else 'No'}")
        print(f"Score: {agent_status['score']}")
        print(f"Percepts: {self.get_percepts()}")

    def get_percepts(self) -> List[str]:
        """Get current percepts based on agent position"""
        percepts = []
        row, col = self.agent.position
        
        # Check adjacent cells
        adjacent = [(row-1,col), (row+1,col), (row,col-1), (row,col+1)]
        for r, c in adjacent:
            if 0 <= r < self.world_size[0] and 0 <= c < self.world_size[1]:
                cell = self.original_world[r][c]
                if cell == 'W' and "Stench" not in percepts:
                    percepts.append("Stench")
                elif cell == 'P' and "Breeze" not in percepts:
                    percepts.append("Breeze")
        
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

    def _move_agent(self, direction: str) -> Tuple[bool, str]:
        """Move agent in specified direction"""
        new_pos = self.agent.get_next_position(direction)
        if not new_pos:
            return False, "Invalid direction"
            
        # Check boundaries
        if not (0 <= new_pos[0] < self.world_size[0] and 
                0 <= new_pos[1] < self.world_size[1]):
            return False, "Cannot move outside world"
        
        # Move agent
        self.agent.move(direction)
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

    def _update_board_state(self) -> None:
        """Update the game board representation"""
        self.game_world = copy.deepcopy(self.original_world)
        
        # Mark visited cells
        for row, col in self.agent.visited_cells:
            if (row, col) != self.agent.position:
                self.game_world[row][col] = self.agent.agent_config.trail_symbol
        
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

    def get_game_state(self) -> Dict:
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

    def reset(self) -> None:
        """Reset game to initial state"""
        self.original_world = copy.deepcopy(self.world_loader.get_board())
        self.game_world = copy.deepcopy(self.original_world)
        self.agent.reset()
        self.game_over = False
        self.won = False
        self.step_count = 0
        self._place_agent_on_board()
        self._update_display("Game reset")

    def run_autonomous(self) -> None:
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
                time.sleep(0.5)
                continue
                
            print(f"Action: {action} {reason} - {message}")
            time.sleep(0.5)