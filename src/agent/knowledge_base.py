from typing import Set, Tuple, List, Dict
from collections import defaultdict
from .logic import ResolutionProver, PropositionalLogic

class KnowledgeBase:
    def __init__(self):
        # Safe locations (no pit or wumpus)
        self.prover = ResolutionProver()
        # Add Wumpus–Pit mutual exclusivity
        for x in range(10):
            for y in range(10):
                w = PropositionalLogic.to_propositional((x, y), 'W')
                p = PropositionalLogic.to_propositional((x, y), 'P')
                self.prover.add_clause([f"¬{w}", f"¬{p}"])  # ¬W ∨ ¬P = can't be both

        # There is only ONE Wumpus — so at most one Wumpus cell
        wumpus_symbols = [PropositionalLogic.to_propositional((x, y), 'W') for x in range(10) for y in range(10)]
        for i in range(len(wumpus_symbols)):
            for j in range(i + 1, len(wumpus_symbols)):
                self.prover.add_clause([f"¬{wumpus_symbols[i]}", f"¬{wumpus_symbols[j]}"])  # ¬W_i ∨ ¬W_j

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
        if position in self.percept_history:
            return  # Already processed this percept

        self.visited.add(position)
        self.percept_history[position] = percepts
        self.safe_locations.add(position)  # If we're alive, this place is safe

        # Mark adjacent cells as safe if there's no hazard indicator
        if "Stench" not in percepts:
            self._mark_adjacent_safe(position, 'wumpus')
        if "Breeze" not in percepts:
            self._mark_adjacent_safe(position, 'pit')

        # Logical clauses: Stench
        stench_sym = PropositionalLogic.to_propositional(position, 'S')
        if "Stench" in percepts:
            self.prover.add_clause([stench_sym])
            wumpus_neighbors = [
                PropositionalLogic.to_propositional(pos, 'W') 
                for pos in self._get_adjacent(position)
            ]
            self.prover.add_clause([f"¬{stench_sym}"] + wumpus_neighbors)
            for wumpus_sym in wumpus_neighbors:
                self.prover.add_clause([f"¬{wumpus_sym}", stench_sym])
        else:
            self.prover.add_clause([f"¬{stench_sym}"])

        # Logical clauses: Breeze
        breeze_sym = PropositionalLogic.to_propositional(position, 'B')
        if "Breeze" in percepts:
            pit_neighbors = [
                PropositionalLogic.to_propositional(pos, 'P')
                for pos in self._get_adjacent(position)
            ]
            self.prover.add_clause([f"¬{breeze_sym}"] + pit_neighbors)
            for pit_sym in pit_neighbors:
                self.prover.add_clause([f"¬{pit_sym}", breeze_sym])
        else:
            self.prover.add_clause([f"¬{breeze_sym}"])

        # Use resolution to try to prove Wumpus positions
        for neighbor in self._get_adjacent(position):
            w_sym = PropositionalLogic.to_propositional(neighbor, 'W')
            if neighbor not in self.confirmed_wumpus and self.prover.prove(w_sym):
                self.confirmed_wumpus.add(neighbor)
                print(f"[LOGIC] Wumpus definitely at {neighbor}")
            elif self.prover.prove(f"¬{w_sym}"):
                self.safe_locations.add(neighbor)





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
        """Use resolution to infer Wumpus positions"""
        print(f"[LOGIC DEBUG] Safe: {self.safe_locations}, Confirmed Wumpus: {self.confirmed_wumpus}")
        for row in range(10):
            for col in range(10):
                pos = (row, col)
                wumpus_sym = PropositionalLogic.to_propositional(pos, 'W')

                if self.prover.prove(wumpus_sym):
                    self.confirmed_wumpus.add(pos)
                elif self.prover.prove(f"¬{wumpus_sym}"):
                    self.safe_locations.add(pos)



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

    def infer_from_logic(self) -> None:
        """Infer hazards from logical deductions using the prover"""
        for row in range(10):
            for col in range(10):
                pos = (row, col)
                w_sym = PropositionalLogic.to_propositional(pos, 'W')
                if self.prover.prove(w_sym):
                    self.confirmed_wumpus.add(pos)
                elif self.prover.prove(f"¬{w_sym}"):
                    self.safe_locations.add(pos)

    def _resolve_conflicts(self) -> None:
        """Resolve any contradictions in KB"""
        # Ensure no cell is marked as both safe and hazardous
        self.confirmed_wumpus = self.confirmed_wumpus - self.safe_locations
        self.confirmed_pits = self.confirmed_pits - self.safe_locations
