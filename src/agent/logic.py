from typing import List, Set, Tuple, Dict, Optional
from collections import deque, defaultdict

class ResolutionProver:
    def __init__(self):
        self.clauses: Set[frozenset] = set()
        self.symbols: Set[str] = set()
        self._index: Dict[str, Set[frozenset]] = defaultdict(set)  # For faster resolution

    def add_clause(self, clause: List[str]) -> None:
        """Add a disjunctive clause to the KB - skip tautologies"""
        # Check for tautology (a literal and its negation both present)
        literals = set()
        for lit in clause:
            if lit.startswith('¬'):
                base = lit[1:]
                if base in literals:
                    return  # Tautology found
                literals.add(lit)
            else:
                if f"¬{lit}" in literals:
                    return  # Tautology found
                literals.add(lit)
        
        # Proceed with adding non-tautological clause
        frozen = frozenset(clause)
        if frozen not in self.clauses:
            self.clauses.add(frozen)
            for literal in clause:
                self.symbols.add(literal.strip('¬'))

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
            sub_queries = [q.strip() for q in query.split(" OR ")]
            return any(self.prove(sub_query, max_steps) for sub_query in sub_queries)
        
        # Standard resolution for atomic queries
        negated = f"¬{query}" if not query.startswith('¬') else query[1:]
        new_clauses = set(self.clauses)
        new_clauses.add(frozenset([negated]))
        
        seen = set(new_clauses)
        queue = deque(new_clauses)
        steps = 0
        
        while queue and steps < max_steps:
            current = queue.popleft()
            
            # Check against all existing clauses
            for clause in list(seen):
                # Find complementary literals
                resolvents = set()
                for lit in current:
                    complement = f"¬{lit}" if not lit.startswith('¬') else lit[1:]
                    if complement in clause:
                        # Create resolvent by combining and removing complements
                        resolvent = (current | clause) - {lit, complement}
                        
                        # Empty clause means contradiction found
                        if not resolvent:
                            return True
                        
                        # Skip trivial or already seen clauses
                        if resolvent and resolvent not in seen:
                            resolvents.add(resolvent)
                
                # Add new resolvents to processing queue
                for resolvent in resolvents:
                    seen.add(resolvent)
                    queue.append(resolvent)
            
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
    def to_propositional(position: Tuple[int, int], element: str) -> str:
        """Convert grid position to propositional symbol"""
        x, y = position
        return f"{element}_{x}_{y}"

    @staticmethod
    def generate_initial_clauses(world_size: Tuple[int, int]) -> List[List[str]]:
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
