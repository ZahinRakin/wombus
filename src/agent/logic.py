from typing import List, Set, FrozenSet, Dict, Optional
from collections import defaultdict, deque
import logging


class ResolutionProver:
    def __init__(self):
        self.clauses: Set[FrozenSet[str]] = set()
        self.symbols: Set[str] = set()
        self._literal_index: Dict[str, Set[FrozenSet]] = defaultdict(set)  # New index for faster resolution

    def add_clause(self, clause: List[str]) -> None:
        """Improved with input validation and tautology detection"""
        if not clause:
            raise ValueError("Empty clause provided")
        
        # Tautology check (A ∨ ¬A)
        seen = set()
        for lit in clause:
            neg = lit[1:] if lit.startswith('¬') else f"¬{lit}"
            if neg in seen:
                return  # Skip tautologies
            seen.add(lit)
        
        frozen = frozenset(clause)
        if frozen not in self.clauses:
            self.clauses.add(frozen)
            for lit in clause:
                self.symbols.add(lit.strip('¬'))
                self._literal_index[lit].add(frozen)  # Maintain index

    def resolve(self, c1: frozenset, c2: frozenset) -> Set[frozenset]:
        """Efficient resolution focusing only on complementary literals"""
        resolvents = set()
        
        # Only check literals that have complements in the other clause
        for lit in c1:
            comp_lit = f"¬{lit}" if not lit.startswith('¬') else lit[1:]
            if comp_lit in c2:
                resolvent = (c1 | c2) - {lit, comp_lit}
                if resolvent:  # Only add non-empty clauses
                    resolvents.add(frozenset(resolvent))
                else:  # Empty clause found
                    return {frozenset()}
        return resolvents



    def prove(self, query: str, max_steps: int = 1000) -> bool:
        """
        Use resolution refutation to prove the query.
        Handles both atomic and disjunctive queries.
        
        Args:
            query: The query to prove (e.g., "A" or "A OR B OR C")
            max_steps: Maximum resolution steps to prevent infinite loops
            
        Returns:
            bool: True if the query can be proven, False otherwise
        """
        # Handle disjunctive queries (A OR B OR C)
        if " OR " in query:
            return any(self.prove(sub_query.strip(), max_steps) 
                    for sub_query in query.split(" OR "))
        
        # Standard resolution for atomic queries
        negated = f"¬{query}" if not query.startswith('¬') else query[1:]
        new_clauses = set(self.clauses)
        new_clauses.add(frozenset([negated]))
        
        # Create resolution index
        index = defaultdict(set)
        for clause in new_clauses:
            for lit in clause:
                index[lit].add(clause)
        
        seen = set(new_clauses)
        queue = deque(new_clauses)
        steps = 0
        
        while queue and steps < max_steps:
            current = queue.popleft()
            
            # Get all literals to check for resolution
            for lit in current:
                complement = lit[1:] if lit.startswith('¬') else f"¬{lit}"
                
                # Resolve with all clauses containing the complement
                for other_clause in index.get(complement, set()):
                    # Skip if we've already processed this pair
                    if other_clause in seen:
                        continue
                    
                    # Create resolvent by combining and removing complements
                    resolvent = (current | other_clause) - {lit, complement}
                    
                    # Empty clause means contradiction found
                    if not resolvent:
                        return True
                    
                    # Add new resolvent if not already seen
                    if resolvent not in seen:
                        seen.add(resolvent)
                        queue.append(resolvent)
                        # Update index
                        for l in resolvent:
                            index[l].add(resolvent)
            
            steps += 1
        
        return False



    def get_entailed_literals(self) -> Set[str]:
        """Find all literals that are entailed by the KB"""
        entailed = set()
        for symbol in self.symbols:
            if self.prove(symbol):
                entailed.add(symbol)
            if self.prove(f"¬{symbol}"):
                entailed.add(f"¬{symbol}")
        return entailed

class PropositionalLogic:
    @staticmethod
    def to_propositional(position: tuple[int, int], element: str) -> str:
        """Convert grid position to propositional symbol"""
        x, y = position
        return f"{element}_{x}_{y}"

    @staticmethod
    def generate_initial_clauses(world_size: tuple[int, int]) -> List[List[str]]:
        """Generate initial Wumpus World axioms"""
        clauses = []
        rows, cols = world_size

        # Each cell has at most one hazard: ¬W ∨ ¬P
        for x in range(rows):
            for y in range(cols):
                w = PropositionalLogic.to_propositional((x, y), 'W')
                p = PropositionalLogic.to_propositional((x, y), 'P')
                clauses.append([f"¬{w}", f"¬{p}"])

        # Stench ⇔ adjacent Wumpus
        # Breeze ⇔ adjacent Pit
        for x in range(rows):
            for y in range(cols):
                adj = [(x-1,y), (x+1,y), (x,y-1), (x,y+1)]
                valid_adj = [(i,j) for i,j in adj if 0 <= i < rows and 0 <= j < cols]

                # Breeze logic
                breeze = PropositionalLogic.to_propositional((x, y), 'B')
                pit_clause = [f"¬{breeze}"] + [
                    PropositionalLogic.to_propositional((i, j), 'P')
                    for (i, j) in valid_adj
                ]
                clauses.append(pit_clause)
                for pit in pit_clause[1:]:
                    clauses.append([f"¬{pit}", breeze])

                # Stench logic
                stench = PropositionalLogic.to_propositional((x, y), 'S')
                wumpus_clause = [f"¬{stench}"] + [
                    PropositionalLogic.to_propositional((i, j), 'W')
                    for (i, j) in valid_adj
                ]
                clauses.append(wumpus_clause)
                for wumpus in wumpus_clause[1:]:
                    clauses.append([f"¬{wumpus}", stench])

        return clauses
