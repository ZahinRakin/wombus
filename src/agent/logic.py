from typing import List, Set, Tuple, Dict

class ResolutionProver:
    def __init__(self):
        self.clauses: Set[frozenset] = set()
        self.symbols: Set[str] = set()

    def add_clause(self, clause: List[str]) -> None:
        """Add a disjunctive clause to the KB"""
        self.clauses.add(frozenset(clause))
        for literal in clause:
            self.symbols.add(literal.strip('¬'))

    def resolve(self, c1: frozenset, c2: frozenset) -> frozenset:
        """Resolve two clauses"""
        for literal in c1:
            if f"¬{literal}" in c2:
                resolvent = (c1 | c2) - {literal, f"¬{literal}"}
                return frozenset(resolvent)
        return frozenset()

    def prove(self, query: str) -> bool:
        """Use resolution to prove a query"""
        negated_query = f"¬{query}" if '¬' not in query else query[1:]
        clauses = self.clauses | {frozenset([negated_query])}
        
        while True:
            new_clauses = set()
            for c1 in clauses:
                for c2 in clauses:
                    if c1 != c2:
                        resolvent = self.resolve(c1, c2)
                        if not resolvent:  # Empty clause found
                            return True
                        if resolvent not in clauses:
                            new_clauses.add(resolvent)
            
            if not new_clauses:
                return False
            clauses |= new_clauses

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
        
        # Each cell has at most one hazard
        for x in range(rows):
            for y in range(cols):
                # ¬W_x,y ∨ ¬P_x,y
                clauses.append([
                    f"¬{PropositionalLogic.to_propositional((x,y), 'W')}",
                    f"¬{PropositionalLogic.to_propositional((x,y), 'P')}"
                ])
        
        # Breeze and Stench implications
        for x in range(rows):
            for y in range(cols):
                adj = [(x-1,y), (x+1,y), (x,y-1), (x,y+1)]
                valid_adj = [(i,j) for i,j in adj if 0 <= i < rows and 0 <= j < cols]
                
                # Breeze ⇔ adjacent pit
                breeze = PropositionalLogic.to_propositional((x,y), 'B')
                pit_clauses = []
                for (i,j) in valid_adj:
                    pit = PropositionalLogic.to_propositional((i,j), 'P')
                    # B_x,y ⇒ P_i,j
                    clauses.append([f"¬{breeze}", pit])
                    pit_clauses.append(pit)
                # P_i,j ⇒ B_x,y (for all adjacent)
                for pit in pit_clauses:
                    clauses.append([f"¬{pit}", breeze])
                
                # Similar for Stench ⇔ adjacent Wumpus
                # ... (implementation similar to breeze)
        
        return clauses