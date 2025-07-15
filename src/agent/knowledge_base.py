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
        
        # Track unvisited safe locations separately for prioritization
        self.unvisited_safe: Set[Tuple[int, int]] = set()
        
        # Percept history
        self.percept_history: Dict[Tuple[int, int], List[str]] = defaultdict(list)



    def add_percept(self, position: Tuple[int, int], percepts: List[str]) -> None:
        """Update KB with new percepts at given position"""
        if position in self.percept_history:
            return  # Already processed this percept

        print(f"[KB] Processing percepts at {position}: {percepts}")
        
        self.visited.add(position)
        self.percept_history[position] = percepts
        self.safe_locations.add(position)  # If we're alive, this place is safe
        
        # Remove from unvisited_safe since we're visiting it now
        if position in self.unvisited_safe:
            self.unvisited_safe.remove(position)

        # Process each percept type
        has_stench = "Stench" in percepts
        has_breeze = "Breeze" in percepts
        has_glitter = "Glitter" in percepts

        print(f"[KB] Stench: {has_stench}, Breeze: {has_breeze}, Glitter: {has_glitter}")

        # Handle Stench percept
        stench_sym = PropositionalLogic.to_propositional(position, 'S')
        if has_stench:
            print(f"[KB] Adding stench clause at {position}")
            self.prover.add_clause([stench_sym])
            
            # At least one adjacent cell has a wumpus
            wumpus_neighbors = [
                PropositionalLogic.to_propositional(pos, 'W') 
                for pos in self._get_adjacent(position)
            ]
            if wumpus_neighbors:
                # S → (W1 ∨ W2 ∨ ... ∨ Wn) which is ¬S ∨ W1 ∨ W2 ∨ ... ∨ Wn
                self.prover.add_clause([f"¬{stench_sym}"] + wumpus_neighbors)
                
                # Each wumpus implies stench: Wi → S which is ¬Wi ∨ S
                for wumpus_sym in wumpus_neighbors:
                    self.prover.add_clause([f"¬{wumpus_sym}", stench_sym])
                
                # Update possible wumpus positions
                for adj_pos in self._get_adjacent(position):
                    if adj_pos not in self.safe_locations and adj_pos not in self.visited:
                        self.possible_wumpus.add(adj_pos)
                        print(f"[KB] Added {adj_pos} to possible wumpus locations")
        else:
            print(f"[KB] No stench at {position} - marking adjacent cells safe from wumpus")
            self.prover.add_clause([f"¬{stench_sym}"])
            
            # No adjacent wumpus: ¬S → ¬W1 ∧ ¬W2 ∧ ... which is S ∨ ¬Wi for each i
            for adj_pos in self._get_adjacent(position):
                wumpus_sym = PropositionalLogic.to_propositional(adj_pos, 'W')
                self.prover.add_clause([stench_sym, f"¬{wumpus_sym}"])
                # Only mark as globally safe if also safe from pits
                # Remove from possible wumpus if it was there
                if adj_pos in self.possible_wumpus:
                    self.possible_wumpus.remove(adj_pos)
                    print(f"[KB] Removed {adj_pos} from possible wumpus (no stench)")

        # Handle Breeze percept
        breeze_sym = PropositionalLogic.to_propositional(position, 'B')
        if has_breeze:
            print(f"[KB] Adding breeze clause at {position}")
            self.prover.add_clause([breeze_sym])
            
            # At least one adjacent cell has a pit
            pit_neighbors = [
                PropositionalLogic.to_propositional(pos, 'P')
                for pos in self._get_adjacent(position)
            ]
            if pit_neighbors:
                # B → (P1 ∨ P2 ∨ ... ∨ Pn) which is ¬B ∨ P1 ∨ P2 ∨ ... ∨ Pn
                self.prover.add_clause([f"¬{breeze_sym}"] + pit_neighbors)
                
                # Each pit implies breeze: Pi → B which is ¬Pi ∨ B
                for pit_sym in pit_neighbors:
                    self.prover.add_clause([f"¬{pit_sym}", breeze_sym])
                
                # Update possible pit positions
                for adj_pos in self._get_adjacent(position):
                    if adj_pos not in self.safe_locations and adj_pos not in self.visited:
                        self.possible_pits.add(adj_pos)
                        print(f"[KB] Added {adj_pos} to possible pit locations")
        else:
            print(f"[KB] No breeze at {position} - marking adjacent cells safe from pits")
            self.prover.add_clause([f"¬{breeze_sym}"])
            
            # No adjacent pits: ¬B → ¬P1 ∧ ¬P2 ∧ ... which is B ∨ ¬Pi for each i
            for adj_pos in self._get_adjacent(position):
                pit_sym = PropositionalLogic.to_propositional(adj_pos, 'P')
                self.prover.add_clause([breeze_sym, f"¬{pit_sym}"])
                # Only mark as globally safe if also safe from wumpus
                # Remove from possible pits if it was there
                if adj_pos in self.possible_pits:
                    self.possible_pits.remove(adj_pos)
                    print(f"[KB] Removed {adj_pos} from possible pits (no breeze)")

        # Use resolution to try to prove or disprove hazards in adjacent cells
        for neighbor in self._get_adjacent(position):
            if neighbor not in self.visited:
                # Check wumpus
                w_sym = PropositionalLogic.to_propositional(neighbor, 'W')
                if self.prover.prove(w_sym):
                    self.confirmed_wumpus.add(neighbor)
                    print(f"[LOGIC] Wumpus definitely at {neighbor}")
                elif self.prover.prove(f"¬{w_sym}"):
                    self.safe_locations.add(neighbor)
                    self.unvisited_safe.add(neighbor)  # Add to unvisited safe
                    print(f"[LOGIC] No wumpus at {neighbor} - marked safe")
                
                # Check pit
                p_sym = PropositionalLogic.to_propositional(neighbor, 'P')
                if self.prover.prove(p_sym):
                    self.confirmed_pits.add(neighbor)
                    print(f"[LOGIC] Pit definitely at {neighbor}")
                elif self.prover.prove(f"¬{p_sym}"):
                    self.safe_locations.add(neighbor)
                    self.unvisited_safe.add(neighbor)  # Add to unvisited safe
                    print(f"[LOGIC] No pit at {neighbor} - marked safe")

        # Update safe locations based on logical proofs
        self._update_safe_locations()
        
        # Run final inference after all percepts processed
        self._infer_pit_positions()
        self._infer_wumpus_positions()





    def infer_dangers(self) -> None:
        """Use logical inference to determine hazards"""
        self._infer_wumpus_positions()
        self._infer_pit_positions()
        self._resolve_conflicts()

    def get_safe_moves(self, position: Tuple[int, int]) -> List[str]:
        """Return directions to adjacent safe cells, prioritizing unvisited ones"""
        x, y = position
        adjacent = {
            'up': (x-1, y),
            'down': (x+1, y),
            'left': (x, y-1),
            'right': (x, y+1)
        }
        
        # First priority: unvisited safe locations
        unvisited_moves = [
            dir for dir, pos in adjacent.items()
            if pos in self.unvisited_safe
        ]
        
        if unvisited_moves:
            print(f"[DECISION] Found unvisited safe moves: {unvisited_moves}")
            return unvisited_moves
        
        # Second priority: visited safe locations (backtracking)
        visited_moves = [
            dir for dir, pos in adjacent.items()
            if pos in self.safe_locations and pos in self.visited
        ]
        
        if visited_moves:
            print(f"[DECISION] Only visited safe moves available: {visited_moves}")
            return visited_moves
        
        print(f"[DECISION] No safe moves found from {position}")
        return []

    def mark_risky(self, position: Tuple[int, int]) -> None:
        """Mark a position as potentially risky (loop detection)"""
        if position in self.safe_locations:
            self.safe_locations.remove(position)

    def _mark_adjacent_safe(self, position: Tuple[int, int], hazard_type: str) -> None:
        """Mark adjacent cells as safe for specific hazard"""
        x, y = position
        adjacent = [(x-1,y), (x+1,y), (x,y-1), (x,y+1)]
        
        for pos in adjacent:
            if 0 <= pos[0] < 10 and 0 <= pos[1] < 10:  # Check bounds
                if hazard_type == 'wumpus' and pos in self.possible_wumpus:
                    self.possible_wumpus.remove(pos)
                elif hazard_type == 'pit' and pos in self.possible_pits:
                    self.possible_pits.remove(pos)
                
                # Add to safe locations and unvisited if not visited
                self.safe_locations.add(pos)
                if pos not in self.visited:
                    self.unvisited_safe.add(pos)
                print(f"[KB] Marked {pos} as safe from {hazard_type}")

    def _get_adjacent(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = position
        candidates = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        return [(i, j) for i, j in candidates if 0 <= i < 10 and 0 <= j < 10]

    def _infer_wumpus_positions(self) -> None:
        """Infer possible wumpus positions from stench percepts"""
        stench_cells = [pos for pos, percepts in self.percept_history.items() if "Stench" in percepts]
        
        print(f"[KB] _infer_wumpus_positions: stench_cells = {stench_cells}")
        
        if not stench_cells:
            # No stench detected anywhere, so no wumpus suspected
            self.possible_wumpus.clear()
            return

        # Start with adjacent cells of stench locations
        if stench_cells:
            possible = set()
            for stench_pos in stench_cells:
                # Add all unvisited, unsafe adjacent cells as possible wumpus locations
                for neighbor in self._get_adjacent(stench_pos):
                    if (neighbor not in self.safe_locations and 
                        neighbor not in self.visited and 
                        neighbor not in self.confirmed_wumpus):
                        possible.add(neighbor)
                        print(f"[KB] Adding {neighbor} as possible wumpus (adjacent to stench at {stench_pos})")
            
            self.possible_wumpus = possible
            print(f"[KB] Updated possible_wumpus: {self.possible_wumpus}")

        # Also try logical inference
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
        """Infer possible pit positions from breeze percepts"""
        breeze_cells = [pos for pos, percepts in self.percept_history.items() if "Breeze" in percepts]
        
        print(f"[KB] _infer_pit_positions: breeze_cells = {breeze_cells}")
        
        if not breeze_cells:
            # No breeze detected anywhere, so no pits suspected
            self.possible_pits.clear()
            return

        # Start with adjacent cells of breeze locations
        if breeze_cells:
            possible = set()
            for breeze_pos in breeze_cells:
                # Add all unvisited, unsafe adjacent cells as possible pit locations
                for neighbor in self._get_adjacent(breeze_pos):
                    if (neighbor not in self.safe_locations and 
                        neighbor not in self.visited and 
                        neighbor not in self.confirmed_pits):
                        possible.add(neighbor)
                        print(f"[KB] Adding {neighbor} as possible pit (adjacent to breeze at {breeze_pos})")
            
            self.possible_pits = possible
            print(f"[KB] Updated possible_pits: {self.possible_pits}")

    def infer_from_logic(self) -> None:
        """Infer hazards from logical deductions and percept-based reasoning"""
        # First do percept-based inference
        self._infer_pit_positions()
        self._infer_wumpus_positions()
        
        # Then try logical resolution for any remaining unknowns
        for row in range(10):
            for col in range(10):
                pos = (row, col)
                if pos not in self.visited:
                    # Check wumpus
                    w_sym = PropositionalLogic.to_propositional(pos, 'W')
                    if self.prover.prove(w_sym):
                        self.confirmed_wumpus.add(pos)
                        # Remove from possible if confirmed
                        if pos in self.possible_wumpus:
                            self.possible_wumpus.remove(pos)
                    elif self.prover.prove(f"¬{w_sym}"):
                        self.safe_locations.add(pos)
                        # Remove from possible if disproven
                        if pos in self.possible_wumpus:
                            self.possible_wumpus.remove(pos)
                    
                    # Check pit
                    p_sym = PropositionalLogic.to_propositional(pos, 'P')
                    if self.prover.prove(p_sym):
                        self.confirmed_pits.add(pos)
                        # Remove from possible if confirmed
                        if pos in self.possible_pits:
                            self.possible_pits.remove(pos)
                    elif self.prover.prove(f"¬{p_sym}"):
                        self.safe_locations.add(pos)
                        # Remove from possible if disproven
                        if pos in self.possible_pits:
                            self.possible_pits.remove(pos)

    def _resolve_conflicts(self) -> None:
        """Resolve any contradictions in KB"""
        # Ensure no cell is marked as both safe and hazardous
        self.confirmed_wumpus = self.confirmed_wumpus - self.safe_locations
        self.confirmed_pits = self.confirmed_pits - self.safe_locations

    def _update_safe_locations(self) -> None:
        """Update safe_locations using both logical proofs and heuristic safety analysis"""
        # Keep visited locations as safe (we survived them)
        new_safe = set(self.visited)
        new_unvisited_safe = set()
        
        # Add cells that are proven safe from both hazards via logic
        for row in range(10):
            for col in range(10):
                pos = (row, col)
                if pos not in self.visited:
                    # Check if safe from both wumpus and pit via logical proofs
                    w_sym = PropositionalLogic.to_propositional(pos, 'W')
                    p_sym = PropositionalLogic.to_propositional(pos, 'P')
                    
                    # If we can prove no wumpus AND no pit, then it's safe
                    if self.prover.prove(f"¬{w_sym}") and self.prover.prove(f"¬{p_sym}"):
                        new_safe.add(pos)
                        new_unvisited_safe.add(pos)
                        print(f"[LOGIC] Cell {pos} proven safe from both hazards")
        
        # HEURISTIC SAFETY: Add cells that are likely safe based on percept patterns
        self._add_heuristic_safe_locations(new_safe, new_unvisited_safe)
        
        self.safe_locations = new_safe
        self.unvisited_safe = new_unvisited_safe
        print(f"[KB] Updated safe_locations: {self.safe_locations}")
        print(f"[KB] Updated unvisited_safe: {self.unvisited_safe}")
    
    def _add_heuristic_safe_locations(self, safe_set: Set[Tuple[int, int]], unvisited_safe_set: Set[Tuple[int, int]]) -> None:
        """Add heuristically safe locations based on percept analysis"""
        print("[HEURISTIC] Analyzing percept patterns for additional safe cells...")
        
        # Strategy 1: Cells adjacent to "Nothing" percepts are likely safe
        for pos, percepts in self.percept_history.items():
            if percepts == ["Nothing"]:
                for adj_pos in self._get_adjacent(pos):
                    if (adj_pos not in self.visited and 
                        adj_pos not in self.possible_pits and 
                        adj_pos not in self.possible_wumpus and
                        adj_pos not in self.confirmed_pits and
                        adj_pos not in self.confirmed_wumpus):
                        
                        safe_set.add(adj_pos)
                        unvisited_safe_set.add(adj_pos)
                        print(f"[HEURISTIC] Added {adj_pos} as safe (adjacent to clear cell {pos})")
        
        # Strategy 2: If we've identified all wumpus/pit sources for a breeze/stench pattern,
        # other adjacent cells should be safe
        self._identify_pattern_safe_cells(safe_set, unvisited_safe_set)
    
    def _identify_pattern_safe_cells(self, safe_set: Set[Tuple[int, int]], unvisited_safe_set: Set[Tuple[int, int]]) -> None:
        """Identify safe cells through percept pattern analysis"""
        
        # For each stench cell, if we've confirmed the wumpus location,
        # other adjacent cells are safe from wumpus
        for pos, percepts in self.percept_history.items():
            if "Stench" in percepts:
                adjacent_cells = self._get_adjacent(pos)
                confirmed_wumpus_nearby = any(adj in self.confirmed_wumpus for adj in adjacent_cells)
                
                if confirmed_wumpus_nearby:
                    # The wumpus source is identified, other adjacent cells are safe from wumpus
                    for adj_pos in adjacent_cells:
                        if (adj_pos not in self.visited and 
                            adj_pos not in self.confirmed_wumpus and
                            adj_pos not in self.possible_pits and
                            adj_pos not in self.confirmed_pits):
                            
                            # This cell is safe from wumpus, check if also safe from pits
                            if not self._could_have_pit(adj_pos):
                                safe_set.add(adj_pos)
                                unvisited_safe_set.add(adj_pos)
                                print(f"[HEURISTIC] Added {adj_pos} as safe (wumpus source identified)")
        
        # Similar logic for breeze/pit patterns
        for pos, percepts in self.percept_history.items():
            if "Breeze" in percepts:
                adjacent_cells = self._get_adjacent(pos)
                confirmed_pits_nearby = sum(1 for adj in adjacent_cells if adj in self.confirmed_pits)
                possible_pits_nearby = sum(1 for adj in adjacent_cells if adj in self.possible_pits)
                
                # If we have enough confirmed/possible pits to account for the breeze
                if confirmed_pits_nearby >= 1 or (confirmed_pits_nearby + possible_pits_nearby <= 1):
                    for adj_pos in adjacent_cells:
                        if (adj_pos not in self.visited and 
                            adj_pos not in self.confirmed_pits and
                            adj_pos not in self.possible_pits and
                            adj_pos not in self.confirmed_wumpus and
                            adj_pos not in self.possible_wumpus):
                            
                            safe_set.add(adj_pos)
                            unvisited_safe_set.add(adj_pos)
                            print(f"[HEURISTIC] Added {adj_pos} as safe (pit pattern analyzed)")
    
    def _could_have_pit(self, position: Tuple[int, int]) -> bool:
        """Check if a position could potentially have a pit based on breeze patterns"""
        # If this position is adjacent to any breeze cell and not ruled out, it could have a pit
        for breeze_pos, percepts in self.percept_history.items():
            if "Breeze" in percepts and position in self._get_adjacent(breeze_pos):
                if position not in self.confirmed_pits and position in self.possible_pits:
                    return True
        return False

    def get_status_info(self) -> Dict:
        """Return current knowledge base status for debugging"""
        return {
            'visited': self.visited,
            'safe_locations': self.safe_locations,
            'unvisited_safe': self.unvisited_safe,
            'possible_pits': self.possible_pits,
            'possible_wumpus': self.possible_wumpus,
            'confirmed_pits': self.confirmed_pits,
            'confirmed_wumpus': self.confirmed_wumpus
        }
