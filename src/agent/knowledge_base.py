from typing import Set, Tuple, List, Dict
from collections import defaultdict

class KnowledgeBase:
    def __init__(self):
        # Safe locations (no pit or wumpus)
        self.safe_locations: Set[Tuple[int, int]] = set()
        
        # Possible hazard locations
        self.possible_wumpus: Set[Tuple[int, int]] = set()
        self.possible_pits: Set[Tuple[int, int]] = set()
        
        # Confirmed hazards
        self.confirmed_wumpus: Set[Tuple[int, int]] = set()
        self.confirmed_pits: Set[Tuple[int, int]] = set()
        
        # Visited locations
        self.visited: Set[Tuple[int, int]] = set()
        
        # Percept history
        self.percept_history: Dict[Tuple[int, int], List[str]] = defaultdict(list)

    def add_percept(self, position: Tuple[int, int], percepts: List[str]) -> None:
        """Update KB with new percepts at given position"""
        self.visited.add(position)
        self.percept_history[position] = percepts
        
        # Mark current position as safe (since we're alive)
        self.safe_locations.add(position)
        
        if "Stench" not in percepts:
            self._mark_adjacent_safe(position, 'wumpus')
        else:
            # Wumpus is nearby — don't mark adjacent cells safe for wumpus
            pass

        if "Breeze" not in percepts:
            self._mark_adjacent_safe(position, 'pit')
        else:
            # Breeze nearby — don’t assume neighbors are safe from pits
            pass

    def infer_dangers(self) -> None:
        """Use logical inference to determine hazards"""
        self._infer_wumpus_positions()
        self._infer_pit_positions()
        self._resolve_conflicts()

    def get_safe_moves(self, position: Tuple[int, int]) -> List[str]:
        """Return directions to adjacent safe, unvisited cells"""
        x, y = position
        adjacent = {
            'up': (x-1, y),
            'down': (x+1, y),
            'left': (x, y-1),
            'right': (x, y+1)
        }
        
        return [
            dir for dir, pos in adjacent.items()
            if pos in self.safe_locations and pos not in self.visited
        ]

    def mark_risky(self, position: Tuple[int, int]) -> None:
        """Mark a position as potentially risky (loop detection)"""
        if position in self.safe_locations:
            self.safe_locations.remove(position)

    def _mark_adjacent_safe(self, position: Tuple[int, int], hazard_type: str) -> None:
        """Mark adjacent cells as safe for specific hazard"""
        x, y = position
        adjacent = [(x-1,y), (x+1,y), (x,y-1), (x,y+1)]
        
        for pos in adjacent:
            if hazard_type == 'wumpus' and pos in self.possible_wumpus:
                self.possible_wumpus.remove(pos)
            elif hazard_type == 'pit' and pos in self.possible_pits:
                self.possible_pits.remove(pos)
            self.safe_locations.add(pos)

    def _get_adjacent(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = position
        candidates = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        return [(i, j) for i, j in candidates if 0 <= i < 10 and 0 <= j < 10]

    def _infer_wumpus_positions(self) -> None:
        stench_cells = [pos for pos, percepts in self.percept_history.items() if "Stench" in percepts]
        
        if not stench_cells:
            self.possible_wumpus.clear()
            return

        # Get adjacent unvisited and unsafe cells for the first stench cell
        possible = set(
            neighbor for neighbor in self._get_adjacent(stench_cells[0])
            if neighbor not in self.safe_locations and neighbor not in self.visited
        )

        # Intersect with the rest
        for pos in stench_cells[1:]:
            neighbors = set(
                neighbor for neighbor in self._get_adjacent(pos)
                if neighbor not in self.safe_locations and neighbor not in self.visited
            )
            possible &= neighbors

        self.possible_wumpus = possible


    def _infer_pit_positions(self) -> None:
        breeze_cells = [pos for pos, percepts in self.percept_history.items() if "Breeze" in percepts]
        
        if not breeze_cells:
            self.possible_pits.clear()
            return

        possible = set(
            neighbor for neighbor in self._get_adjacent(breeze_cells[0])
            if neighbor not in self.safe_locations and neighbor not in self.visited
        )

        for pos in breeze_cells[1:]:
            neighbors = set(
                neighbor for neighbor in self._get_adjacent(pos)
                if neighbor not in self.safe_locations and neighbor not in self.visited
            )
            possible &= neighbors

        self.possible_pits = possible



    def _resolve_conflicts(self) -> None:
        """Resolve any contradictions in KB"""
        # Ensure no cell is marked as both safe and hazardous
        self.confirmed_wumpus = self.confirmed_wumpus - self.safe_locations
        self.confirmed_pits = self.confirmed_pits - self.safe_locations
