import random
from dataclasses import dataclass
from typing import Set, Tuple, List, Dict, Optional
from .knowledge_base import KnowledgeBase
from .logic import ResolutionProver

@dataclass
class AgentConfig:
    """Configuration settings for the Wumpus World agent."""
    starting_position: Tuple[int, int] = (9, 0)
    movement_cost: int = 1
    arrow_count: int = 1
    arrow_cost: int = 10
    gold_reward: int = 1000
    death_penalty: int = 1000
    win_bonus: int = 500
    agent_symbol: str = 'A'
    trail_symbol: str = '.'
    
    def get_config(self) -> Dict:
        """Return configuration as a dictionary."""
        return {k: v for k, v in self.__dict__.items()}

class Agent:
    """Intelligent agent for navigating the Wumpus World."""
    
    def __init__(self, agent_config: AgentConfig):
        self.agent_config = agent_config
        self.position = agent_config.starting_position
        self.starting_position = agent_config.starting_position
        self.visited_cells: Set[Tuple[int, int]] = {agent_config.starting_position}
        self.arrow_count = agent_config.arrow_count
        self.has_gold = False
        self.is_alive = True
        self.score = 0
        self.action_history: List[str] = []
        self.position_history: List[Tuple[int, int]] = []
        
        # Logical components
        self.knowledge_base = KnowledgeBase()
        self.prover = ResolutionProver()
        
        # Movement directions
        self.directions = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }

    # Core agent methods
    def get_position(self) -> Tuple[int, int]:
        """Return current agent position."""
        return self.position
    
    def set_position(self, new_position: Tuple[int, int]) -> None:
        """Update agent position and mark as visited."""
        self.position = new_position
        self.visited_cells.add(new_position)
    
    def get_next_position(self, direction: str) -> Optional[Tuple[int, int]]:
        """Calculate next position based on movement direction."""
        if direction not in self.directions:
            return None
        
        dr, dc = self.directions[direction]
        row, col = self.position
        if (0 <= row + dr < 10 and 0 <= col + dc < 10):  
            return (row + dr, col + dc)
        print("Invalid move: Out of bounds!")
        return None
    
    def move(self, direction: str) -> Optional[Tuple[int, int]]:
        """Move agent in specified direction."""
        new_position = self.get_next_position(direction)
        if new_position:
            self.set_position(new_position)
            self.score -= self.agent_config.movement_cost
            return new_position
        return None
    
    def grab_gold(self) -> bool:
        """Attempt to pick up gold at current position."""
        if not self.has_gold:
            self.has_gold = True
            self.score += self.agent_config.gold_reward
            return True
        return False
    
    def shoot_arrow(self) -> bool:
        """Fire an arrow if available."""
        if self.arrow_count > 0:
            self.arrow_count -= 1
            self.score -= self.agent_config.arrow_cost
            return True
        return False
    
    def die(self) -> None:
        """Handle agent death."""
        self.is_alive = False
        self.score -= self.agent_config.death_penalty
    
    def is_at_starting_position(self) -> bool:
        """Check if agent is back at starting position."""
        return self.position == self.agent_config.starting_position
    
    def has_won(self) -> bool:
        """Check win condition (has gold and returned to start)."""
        return self.has_gold and self.is_at_starting_position()
    
    # Knowledge and decision making
    def update_knowledge(self, percepts: List[str]) -> None:
        """Update knowledge base with current percepts."""
        self.knowledge_base.add_percept(self.position, percepts)
        self.knowledge_base.infer_dangers()
        self.position_history.append(self.position)
        
        if self._detect_loop():
            self.knowledge_base.mark_risky(self.position)

    def decide_action(self, percepts: List[str]) -> Tuple[str, str]:
        """Determine next action using logical reasoning."""
        self.update_knowledge(percepts)
        
        if "Glitter" in percepts and not self.has_gold:
            return 'grab', "Grabbing gold"
            
        if self.has_gold and self.is_at_starting_position():
            return 'win', "Returned with gold"
            
        if safe_moves := self.knowledge_base.get_safe_moves(self.position):
            return ('move', random.choice(safe_moves))
            
        if self.arrow_count > 0 and self.knowledge_base.possible_wumpus:
            if direction := self._aim_at_wumpus():
                return ('shoot', direction)
                
        if risky_move := self._calculate_risky_move():
            return ('move', risky_move)
            
        return ('wait', "No safe actions available")

    # Helper methods
    def _detect_loop(self) -> bool:
        """Check if agent is stuck in a movement loop."""
        if len(self.position_history) > 8:
            last_four = self.position_history[-4:]
            return last_four == self.position_history[-8:-4]
        return False

    def _aim_at_wumpus(self) -> Optional[str]:
        """Determine best direction to shoot based on KB."""
        # TODO: Implement Wumpus targeting logic
        return None

    def _calculate_risky_move(self) -> Optional[str]:
        """Calculate least risky move when no safe options."""
        # TODO: Implement risk calculation
        return None

    def get_status(self) -> Dict:
        """Return current agent status."""
        return {
            'position': self.position,
            'arrow_count': self.arrow_count,
            'has_gold': self.has_gold,
            'is_alive': self.is_alive,
            'score': self.score,
            'visited_cells': len(self.visited_cells)
        }
    
    def reset(self) -> None:
        """Reset agent to initial state."""
        self.position = self.agent_config.starting_position
        self.visited_cells = {self.agent_config.starting_position}
        self.arrow_count = self.agent_config.arrow_count
        self.has_gold = False
        self.is_alive = True
        self.score = 0
        self.action_history.clear()
        self.position_history.clear()
        self.knowledge_base = KnowledgeBase()

def create_agent() -> Agent:
    """Factory function to create a pre-configured agent."""
    config = AgentConfig(
        starting_position=(9, 0),
        movement_cost=1,
        arrow_count=2,
        arrow_cost=10,
        gold_reward=1000,
        death_penalty=1000,
        agent_symbol='A',
        trail_symbol='.'
    )
    agent = Agent(config)
    
    print("Agent created:")
    print(f"Status: {agent.get_status()}")
    print(f"Config: {config.get_config()}")
    
    # Test movement
    print(f"\nMoving up from {agent.get_position()}")
    if new_pos := agent.move('up'):
        print(f"New position: {new_pos}")
    print(f"Status: {agent.get_status()}")
    
    return agent

if __name__ == "__main__":
    create_agent()