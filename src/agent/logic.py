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
        """Enhanced with OR handling and better resolution"""
        if not query:
            raise ValueError("Empty query provided")
        
        # Handle disjunctive queries (A OR B OR C)
        if " OR " in query:
            return any(self.prove(sub_q.strip(), max_steps) 
                     for sub_q in query.split(" OR "))
        
        negated = f"¬{query}" if not query.startswith('¬') else query[1:]
        new_clauses = set(self.clauses)
        new_clauses.add(frozenset([negated]))
        
        queue = deque(new_clauses)
        seen = set(new_clauses)
        steps = 0
        
        while queue and steps < max_steps:
            current = queue.popleft()
            for lit in current:
                complement = lit[1:] if lit.startswith('¬') else f"¬{lit}"
                for other_clause in self._literal_index.get(complement, set()):
                    resolvents = self.resolve(current, other_clause)
                    for resolvent in resolvents:
                        if not resolvent:  # Empty clause found
                            return True
                        if resolvent not in seen:
                            seen.add(resolvent)
                            queue.append(resolvent)
            steps += 1
        
        return False

    def get_entailed_literals(self) -> Set[str]:
        """Find all literals that are entailed by the KB"""
        return {symbol for symbol in self.symbols if self.prove(symbol) or self.prove(f"¬{symbol}")}

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
