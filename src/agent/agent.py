import random
from dataclasses import dataclass
from typing import Set, Tuple, List, Dict, Optional
from .knowledge_base import KnowledgeBase
from .logic import ResolutionProver

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

    def get_config(self) -> Dict:
        return {k: v for k, v in self.__dict__.items()}

class Agent:
    def __init__(self, agent_config: AgentConfig):
        self.agent_config = agent_config
        self.position = agent_config.starting_position
        self.starting_position = agent_config.starting_position
        self.visited_cells: Set[Tuple[int, int]] = {self.position}
        self.arrow_count = agent_config.arrow_count
        self.has_gold = False
        self.is_alive = True
        self.score = 0
        self.action_history: List[str] = []
        self.position_history: List[Tuple[int, int]] = []

        self.knowledge_base = KnowledgeBase()
        self.prover = ResolutionProver()

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
        self.visited_cells.add(new_position)

    def get_next_position(self, direction: str) -> Optional[Tuple[int, int]]:
        if direction not in self.directions:
            return None
        dr, dc = self.directions[direction]
        row, col = self.position
        if (0 <= row + dr < 10 and 0 <= col + dc < 10):
            return (row + dr, col + dc)
        return None

    def move(self, direction: str) -> Optional[Tuple[int, int]]:
        new_position = self.get_next_position(direction)
        if new_position:
            self.set_position(new_position)
            self.score -= self.agent_config.movement_cost
            return new_position
        return None

    def grab_gold(self) -> bool:
        if not self.has_gold:
            self.has_gold = True
            self.score += self.agent_config.gold_reward
            return True
        return False

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
        return self.has_gold and self.is_at_starting_position()

    def update_knowledge(self, percepts: List[str]) -> None:
        self.knowledge_base.add_percept(self.position, percepts)
        self.knowledge_base.infer_from_logic()
        self.position_history.append(self.position)

        print(f"[KNOWLEDGE] Added percepts at {self.position}: {percepts}")
        print(f"[DEBUG] Possible Wumpus: {self.knowledge_base.possible_wumpus}")
        print(f"[DEBUG] Possible Pits: {self.knowledge_base.possible_pits}")
        print(f"[KNOWLEDGE] Safe locations: {self.knowledge_base.safe_locations}")

    def decide_action(self, percepts: List[str]) -> Tuple[str, str]:
        self.update_knowledge(percepts)

        print(f"[DECISION] At {self.position}, has_gold: {self.has_gold}")

        if "Glitter" in percepts and not self.has_gold:
            print(f"[DECISION] Grabbing gold at {self.position}")
            return 'grab', "Grabbing gold"

        if self.has_gold and self.is_at_starting_position():
            return 'win', "Returned with gold"

        if target := self._find_nearest_unvisited_safe():
            if direction := self._get_direction_to(target):
                print(f"[DECISION] Moving safely toward {target} via {direction}")
                return 'move', direction

        if self.has_gold and not self.is_at_starting_position():
            if direction := self._get_direction_to(self.starting_position):
                print(f"[DECISION] Returning home via {direction}")
                return 'move', direction

        if self.arrow_count > 0 and self.knowledge_base.possible_wumpus:
            if direction := self._aim_at_wumpus():
                print(f"[DECISION] Shooting arrow {direction}")
                return 'shoot', direction

        if direction := self._calculate_risky_move():
            print(f"[DECISION] Taking risky move {direction}")
            return 'move', direction

        print("[DECISION] Waiting — no safe move available")
        return 'wait', "No safe or logical move found"


    def _find_nearest_unvisited_safe(self) -> Optional[Tuple[int, int]]:
        from collections import deque
        queue = deque([(self.position, [])])
        visited = {self.position}
        while queue:
            current, path = queue.popleft()
            if current in self.knowledge_base.safe_locations and current not in self.visited_cells:
                return current
            for dr, dc in self.directions.values():
                nr, nc = current[0] + dr, current[1] + dc
                neighbor = (nr, nc)
                if 0 <= nr < 10 and 0 <= nc < 10 and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    def _get_direction_to(self, target: Tuple[int, int]) -> Optional[str]:
        """Find the direction to move toward a target position"""
        from collections import deque
        queue = deque([(self.position, [])])
        visited = {self.position}
        while queue:
            current, path = queue.popleft()
            if current == target:
                if path:
                    dr, dc = path[0]
                    for direction, (drow, dcol) in self.directions.items():
                        if (dr, dc) == (drow, dcol):
                            return direction
            for direction, (dr, dc) in self.directions.items():
                neighbor = (current[0] + dr, current[1] + dc)
                if (0 <= neighbor[0] < 10 and 0 <= neighbor[1] < 10 and
                        neighbor not in visited and
                        neighbor not in self.knowledge_base.confirmed_wumpus and
                        neighbor not in self.knowledge_base.confirmed_pits and
                        neighbor not in self.knowledge_base.possible_wumpus and
                        neighbor not in self.knowledge_base.possible_pits):
                    visited.add(neighbor)
                    queue.append((neighbor, path + [(dr, dc)]))
        return None

    def _detect_loop(self) -> bool:
        if len(self.position_history) > 8:
            return self.position_history[-4:] == self.position_history[-8:-4]
        return False

    def _aim_at_wumpus(self) -> Optional[str]:
        if not self.knowledge_base.possible_wumpus:
            return None
        wr, wc = next(iter(self.knowledge_base.possible_wumpus))
        ar, ac = self.position
        if wr == ar:
            return 'right' if wc > ac else 'left'
        elif wc == ac:
            return 'down' if wr > ar else 'up'
        return None

    def _calculate_risky_move(self) -> Optional[str]:
        """Calculate a risky move"""
        for direction, (dr, dc) in self.directions.items():
            nr, nc = self.position[0] + dr, self.position[1] + dc
            pos = (nr, nc)
            if 0 <= nr < 10 and 0 <= nc < 10 and pos not in self.visited_cells:
                return direction
        return None


    def get_status(self) -> Dict:
        return {
            'position': self.position,
            'arrow_count': self.arrow_count,
            'has_gold': self.has_gold,
            'is_alive': self.is_alive,
            'score': self.score,
            'visited_cells': len(self.visited_cells)
        }

    def reset(self) -> None:
        self.position = self.starting_position
        self.visited_cells = {self.starting_position}
        self.arrow_count = self.agent_config.arrow_count
        self.has_gold = False
        self.is_alive = True
        self.score = 0
        self.action_history.clear()
        self.position_history.clear()
        self.knowledge_base = KnowledgeBase()
