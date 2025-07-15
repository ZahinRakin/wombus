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
        self.visited_cells: Set[Tuple[int, int]] = {self.position} # this won't be needed. since i update the self.original_world in game.py. update it later
        self.path: List[Tuple[int, int]] = []
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

    def move(self, pos) -> Optional[Tuple[int, int]]:
        new_position = pos
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

    def update_knowledge(self, percepts: str) -> None:
        self.knowledge_base.add_percept(self.position, percepts)
        self.knowledge_base.infer_from_logic()
        self.position_history.append(self.position)

        print(f"[KNOWLEDGE] Added percepts at {self.position}: {percepts}")
        print(f"[KNOWLEDGE] Possible Wumpus: {self.knowledge_base.possible_wumpus}")
        print(f"[KNOWLEDGE] Possible Pits: {self.knowledge_base.possible_pits}")
        print(f"[KNOWLEDGE] Safe locations: {self.knowledge_base.safe_locations}")

    def decide_action(self, percepts: str) -> Tuple[str, str]:
        self.update_knowledge(percepts)

        print(f"[DECISION] At {self.position}, has_gold: {self.has_gold}")
        
        # Show current knowledge state
        status = self.knowledge_base.get_status_info()
        print(f"[STATUS] Unvisited safe locations: {status['unvisited_safe']}")
        print(f"[STATUS] All safe locations: {status['safe_locations']}")

        if "Glitter" in percepts and not self.has_gold:
            print(f"[DECISION] Grabbing gold at {self.position}")
            return 'grab', "Grabbing gold"

        if self.has_gold and self.is_at_starting_position():
            return 'win', "Returned with gold"

        # Use the new prioritized safe moves method
        safe_moves = self.knowledge_base.get_safe_moves(self.position)
        if safe_moves:
            direction = safe_moves[0]  # Take first safe move
            print(f"[DECISION] Moving safely {direction}")
            return 'move', direction

        if self.has_gold and not self.is_at_starting_position():
            if direction := self._get_direction_to(self.starting_position):
                print(f"[DECISION] Returning home via {direction}")
                return 'move', direction

        # FRONTIER EXPLORATION: If no safe moves, try to explore frontier
        if direction := self._explore_frontier():
            print(f"[DECISION] Exploring frontier {direction}")
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
        from collections import deque
        queue = deque([(self.position, [])])
        visited = {self.position}
        while queue:
            current, path = queue.popleft()
            if current == target and path:
                prev, curr = path[0], current
                for dir, (dr, dc) in self.directions.items():
                    if (self.position[0] + dr, self.position[1] + dc) == prev:
                        return dir
            for direction, (dr, dc) in self.directions.items():
                nr, nc = current[0] + dr, current[1] + dc
                neighbor = (nr, nc)
                if 0 <= nr < 10 and 0 <= nc < 10 and neighbor in self.knowledge_base.safe_locations and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    def _explore_frontier(self) -> Optional[str]:
        """
        Frontier-based exploration: Find the safest unexplored cell adjacent to known safe areas
        This breaks loops by systematically exploring the boundary of known safe territory
        """
        print("[FRONTIER] Looking for frontier exploration opportunities...")
        
        # Find all frontier cells (unvisited cells adjacent to visited safe cells)
        frontier_candidates = []
        
        for safe_pos in self.knowledge_base.safe_locations:
            if safe_pos in self.visited_cells:  # Only consider visited safe cells as frontier base
                for dr, dc in self.directions.values():
                    nr, nc = safe_pos[0] + dr, safe_pos[1] + dc
                    neighbor = (nr, nc)
                    
                    # Check if this neighbor is a valid frontier cell
                    if (0 <= nr < 10 and 0 <= nc < 10 and 
                        neighbor not in self.visited_cells and
                        neighbor not in self.knowledge_base.confirmed_pits and
                        neighbor not in self.knowledge_base.confirmed_wumpus):
                        
                        # Calculate risk score for this frontier cell
                        risk_score = self._calculate_risk_score(neighbor)
                        frontier_candidates.append((neighbor, risk_score, safe_pos))
        
        if not frontier_candidates:
            print("[FRONTIER] No frontier candidates found")
            return None
        
        # Sort by risk score (lower is better) and distance from current position
        frontier_candidates.sort(key=lambda x: (x[1], self._manhattan_distance(self.position, x[0])))
        
        print(f"[FRONTIER] Found {len(frontier_candidates)} frontier candidates")
        for pos, risk, base in frontier_candidates[:3]:  # Show top 3
            print(f"[FRONTIER] {pos} (risk: {risk}, base: {base})")
        
        # Try to move to the safest frontier cell
        target_pos, _, _ = frontier_candidates[0]
        
        # Check if we can move directly to this frontier cell
        for direction, (dr, dc) in self.directions.items():
            nr, nc = self.position[0] + dr, self.position[1] + dc
            if (nr, nc) == target_pos:
                print(f"[FRONTIER] Direct move to frontier cell {target_pos}")
                return direction
        
        # If not directly reachable, find path to the frontier through safe cells
        path_direction = self._get_direction_to_frontier(target_pos)
        if path_direction:
            print(f"[FRONTIER] Moving towards frontier via {path_direction}")
            return path_direction
        
        print("[FRONTIER] No path to frontier found")
        return None
    
    def _calculate_risk_score(self, position: Tuple[int, int]) -> float:
        """Calculate risk score for a position (lower is safer)"""
        risk = 0.0
        
        # Higher risk if it's a possible pit or wumpus location
        if position in self.knowledge_base.possible_pits:
            risk += 0.5
        if position in self.knowledge_base.possible_wumpus:
            risk += 0.7
        
        # Lower risk if adjacent to more safe cells
        safe_neighbors = sum(1 for adj in self._get_adjacent_positions(position) 
                           if adj in self.knowledge_base.safe_locations)
        risk -= safe_neighbors * 0.1
        
        return risk
    
    def _get_adjacent_positions(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid adjacent positions"""
        r, c = position
        adjacent = []
        for dr, dc in self.directions.values():
            nr, nc = r + dr, c + dc
            if 0 <= nr < 10 and 0 <= nc < 10:
                adjacent.append((nr, nc))
        return adjacent
    
    def _manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _get_direction_to_frontier(self, target: Tuple[int, int]) -> Optional[str]:
        """Find direction to move towards a frontier target through safe cells"""
        from collections import deque
        
        queue = deque([(self.position, [])])
        visited = {self.position}
        
        while queue:
            current, path = queue.popleft()
            
            # If we found a path to target, return first move
            if current == target and path:
                first_move = path[0]
                for direction, (dr, dc) in self.directions.items():
                    if (self.position[0] + dr, self.position[1] + dc) == first_move:
                        return direction
            
            # Explore safe neighbors
            for direction, (dr, dc) in self.directions.items():
                nr, nc = current[0] + dr, current[1] + dc
                neighbor = (nr, nc)
                
                if (0 <= nr < 10 and 0 <= nc < 10 and 
                    neighbor not in visited and
                    (neighbor in self.knowledge_base.safe_locations or neighbor == target)):
                    visited.add(neighbor)
                    new_path = path + [neighbor] if path else [neighbor]
                    queue.append((neighbor, new_path))
        
        return None

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
        for direction, (dr, dc) in self.directions.items():
            nr, nc = self.position[0] + dr, self.position[1] + dc
            pos = (nr, nc)

            if (
                0 <= nr < 10 and 0 <= nc < 10 and
                pos not in self.visited_cells and
                pos not in self.knowledge_base.confirmed_wumpus and
                pos not in self.knowledge_base.confirmed_pits and
                pos not in self.knowledge_base.possible_wumpus and
                pos not in self.knowledge_base.possible_pits
            ):
                print(f"[RISK CHECK] Considering risky but unexplored cell {pos}")
                return direction

        print("[RISK CHECK] No acceptable risky moves found")
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
