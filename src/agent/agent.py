import random
import time
from dataclasses import dataclass
from typing import Set, Tuple, List, Dict, Optional
from ..utils.constants import percepts

@dataclass
class AgentConfig:
    starting_position: Tuple[int, int] = (9, 0)
    movement_cost: int = 1
    arrow_count: int = 1
    arrow_cost: int = 10
    gold_reward: int = 1000
    death_penalty: int = 1000
    win_bonus: int = 500
    agent_symbol: str = 'A'
    trail_symbol: str = '.'
    expected_gold_count: int = 1

    def get_config(self) -> Dict:
        return {k: v for k, v in self.__dict__.items()}

class Agent:
    def __init__(self, agent_config: AgentConfig):
        self.agent_config = agent_config
        self.position = agent_config.starting_position
        self.starting_position = agent_config.starting_position
        self.path: List[Tuple[int, int]] = [self.position]
        self.arrow_count = agent_config.arrow_count
        self.gold_count = 0
        self.must_move = False
        self.is_alive = True
        self.score = 0
        self.action_history: List[str] = []
        self.position_history: List[Tuple[int, int]] = []

        self.directions = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }

    def get_position(self) -> Tuple[int, int]:
        return self.position

    def set_position(self, new_position: Tuple[int, int]) -> None:
        self.position = new_position

    def get_next_position(self, direction: str) -> Optional[Tuple[int, int]]:
        if direction not in self.directions:
            return None
        dr, dc = self.directions[direction]
        row, col = self.position
        if 0 <= row + dr < 10 and 0 <= col + dc < 10:
            return (row + dr, col + dc)
        return None

    def move(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        if pos:
            self.set_position(pos)
            self.score -= self.agent_config.movement_cost
            self.path.append(pos)
            return pos
        return None

    def grab_gold(self) -> bool:
        self.gold_count += 1
        self.score += self.agent_config.gold_reward
        return True
     

    def shoot_arrow(self) -> bool:
        if self.arrow_count > 0:
            self.arrow_count -= 1
            self.score -= self.agent_config.arrow_cost
            return True
        return False

    def die(self) -> None:
        self.is_alive = False
        self.score -= self.agent_config.death_penalty

    def is_at_starting_position(self) -> bool:
        return self.position == self.starting_position

    def has_won(self) -> bool:
        return self.gold_count == self.agent_config.expected_gold_count
   
    def get_random_direction(self) -> str:
        d_int = random.randint(1, 4)
        if d_int == 1:
            return "left"
        if d_int == 2:
            return "right"
        if d_int == 3:
            return "up"
        if d_int == 4:
            return "down"
        return "right"

    def infer_wumpus_shoot(self, neighbors) -> Tuple[str, str]:
        global percepts
        pot_cell = set()
        for neighbor in neighbors:
            r, c = neighbor
            if 'W?' in percepts[r][c]:
                pot_cell.add(self._get_direction_to(neighbor))
        if len(pot_cell) == 1:
            return "shoot", pot_cell.pop()
        if len(pot_cell) > 1 and self.must_move:
            return "shoot", random.choice(list(pot_cell))
        return "pass", "pass"

    def infer_pit(self, neighbors) -> None:
        global percepts
        pot_cell = set()
        for neighbor in neighbors:
            r, c = neighbor
            if 'P?' in percepts[r][c]:
                pot_cell.add((r, c))
        if len(pot_cell) == 1:
            r, c = pot_cell.pop()
            percepts[r][c] = percepts[r][c].replace('P?', 'P')

    def _get_direction_to(self, target: Tuple[int, int]) -> Optional[str]:
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        if dx == 0:
            return 'right' if dy > 0 else 'left'
        if dy == 0:
            return 'down' if dx > 0 else 'up'
        return None


    def get_neighbors(self) -> List[Tuple[int, int]]:
        neighbors = []
        for dr, dc in self.directions.values():
            nr, nc = self.position[0] + dr, self.position[1] + dc
            if 0 <= nr < 10 and 0 <= nc < 10:
                neighbors.append((nr, nc))
        return neighbors

    def decide_action(self, percept: str) -> Tuple[str, str]:
        global percepts
        time.sleep(0.5)

        if self.gold_count == self.agent_config.expected_gold_count:
            return 'win', "congratulations!"

        if 'G' in percept and '~G' not in percept:
            return 'grab', "Grabbing gold"

        neighbors = self.get_neighbors()

        # Try moving to safe unvisited neighbors
        for r, c in neighbors:
            if 'V' not in percepts[r][c] and '~W' in percepts[r][c] and '~P' in percepts[r][c]:
                direction = self._get_direction_to((r, c))
                if direction:
                    return 'move', direction

        # Add inference if breeze or stench is detected
        if 'S' in percept:
            for r, c in neighbors:
                if 'V' in percepts[r][c]:
                    percepts[r][c] += '~W'
                else:
                    if 'W?' not in percepts[r][c]:
                        percepts[r][c] += 'W?'

        if 'B' in percept:
            for r, c in neighbors:
                if 'V' in percepts[r][c]:
                    percepts[r][c] += '~P'
                else:
                    if 'P?' not in percepts[r][c]:
                        percepts[r][c] += 'P?'

        self.infer_pit(neighbors)
        if self.arrow_count > 0:
            action, dir = self.infer_wumpus_shoot(neighbors)
            if action != "pass":
                return action, dir

        # Explore unknown neighbors if no threat known
        for r, c in neighbors:
            if 'V' not in percepts[r][c] and 'W?' not in percepts[r][c] and 'P?' not in percepts[r][c]:
                direction = self._get_direction_to((r, c))
                if direction:
                    return 'move', direction

        # Rollback only if there's something to rollback to
        if len(self.path) > 1:
            return 'move', 'rollback'

        return 'move', self.get_random_direction() # random.


    def get_status(self) -> Dict:
        return {
            'position': self.position,
            'arrow_count': self.arrow_count,
            'gold_count': self.gold_count,
            'is_alive': self.is_alive,
            'score': self.score,
        }

    def reset(self) -> None:
        self.position = self.starting_position
        self.arrow_count = self.agent_config.arrow_count
        self.gold_count = 0
        self.is_alive = True
        self.score = 0
        self.path = [self.starting_position]
        self.action_history.clear()
        self.position_history.clear()
