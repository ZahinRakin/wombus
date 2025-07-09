import unittest
from collections import deque
from typing import Set, Dict, FrozenSet
# from agent.logic import ResolutionProver
import unittest
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agent.logic import ResolutionProver

class TestResolutionProver(unittest.TestCase):
    def setUp(self):
        self.prover = ResolutionProver()

    # Basic Functionality Tests
    def test_empty_knowledge_base(self):
        """Empty KB should prove nothing"""
        self.assertFalse(self.prover.prove("A"))
        self.assertFalse(self.prover.prove("¬A"))

    def test_single_fact(self):
        """KB with single fact should prove that fact"""
        self.prover.add_clause(["A"])
        self.assertTrue(self.prover.prove("A"))
        self.assertFalse(self.prover.prove("¬A"))

    def test_contradiction_handling(self):
        """Contradictions should make everything provable"""
        self.prover.add_clause(["A"])
        self.prover.add_clause(["¬A"])
        self.assertTrue(self.prover.prove("B"))  # Anything provable
        self.assertTrue(self.prover.prove("¬B"))

    # Logical Operation Tests
    def test_implication(self):
        """Test basic implication (P → Q)"""
        self.prover.add_clause(["¬P", "Q"])  # P → Q
        self.prover.add_clause(["P"])
        self.assertTrue(self.prover.prove("Q"))

    def test_disjunctive_queries(self):
        """Test OR queries"""
        self.prover.add_clause(["A", "B"])
        self.assertTrue(self.prover.prove("A OR B"))
        self.assertTrue(self.prover.prove("A OR C"))  # Since A is possible
        self.assertFalse(self.prover.prove("C OR D"))

    def test_chain_reasoning(self):
        """Test multi-step reasoning (P → Q → R)"""
        self.prover.add_clause(["¬P", "Q"])
        self.prover.add_clause(["¬Q", "R"])
        self.prover.add_clause(["P"])
        self.assertTrue(self.prover.prove("R"))

    # Tautology and Special Cases
    def test_tautology_handling(self):
        """Tautologies should be ignored"""
        initial_count = len(self.prover.clauses)
        self.prover.add_clause(["A", "¬A"])  # Tautology
        self.assertEqual(len(self.prover.clauses), initial_count)

    def test_duplicate_clauses(self):
        """Duplicate clauses should be ignored"""
        self.prover.add_clause(["A", "B"])
        self.prover.add_clause(["B", "A"])  # Duplicate
        self.assertEqual(len(self.prover.clauses), 1)

    # Wumpus World Specific Tests
    def test_wumpus_adjacent_inference(self):
        """Test Wumpus adjacency reasoning"""
        # Wumpus causes stench in adjacent cells
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            self.prover.add_clause([f"¬W_1_1", f"S_{1+dx}_{1+dy}"])
        
        # Stench implies at least one Wumpus nearby
        adjacent = ["W_1_1", "W_1_2", "W_2_1", "W_1_0", "W_0_1"]
        self.prover.add_clause(["¬S_1_1"] + adjacent)
        
        # Current observations
        self.prover.add_clause(["S_1_1"])
        self.prover.add_clause(["¬W_1_2"])
        self.prover.add_clause(["¬W_2_1"])
        self.prover.add_clause(["¬W_1_0"])
        self.prover.add_clause(["¬W_0_1"])
        
        self.assertTrue(self.prover.prove("W_1_1"))

    def test_safe_cell_inference(self):
        """Test safe cell deduction"""
        # If no stench, adjacent cells are safe
        adjacent_positions = [(1,0), (0,1), (2,1), (1,2)]
        
        for x, y in adjacent_positions:
            self.prover.add_clause([f"S_1_1", f"¬W_{x}_{y}"])  # No stench → no Wumpus
        
        self.prover.add_clause(["¬S_1_1"])  # No stench
        
        for x, y in adjacent_positions:
            self.assertTrue(self.prover.prove(f"¬W_{x}_{y}"),
                          f"Failed to prove W_{x}_{y} is safe")

    # Performance and Edge Cases
    def test_large_knowledge_base(self):
        """Test with many clauses"""
        for i in range(100):
            self.prover.add_clause([f"A_{i}", f"B_{i}"])
            self.prover.add_clause([f"¬B_{i}", f"C_{i}"])
        
        self.prover.add_clause(["A_0"])
        self.assertTrue(self.prover.prove("C_0"))

    def test_max_steps_handling(self):
        """Test the max_steps parameter"""
        # Create an unsolvable configuration
        for i in range(100):
            self.prover.add_clause([f"X_{i}", f"Y_{i}"])
            self.prover.add_clause([f"¬X_{i}", f"Z_{i}"])
            self.prover.add_clause([f"¬Y_{i}", f"¬Z_{i}"])
        
        # This should not be provable within 50 steps
        self.assertFalse(self.prover.prove("W_99", max_steps=50))

    # Negative Test Cases
    def test_unprovable_queries(self):
        """Test queries that shouldn't be provable"""
        self.prover.add_clause(["A", "B"])
        self.assertFalse(self.prover.prove("A"))
        self.assertFalse(self.prover.prove("B"))

    def test_invalid_input_handling(self):
        """Test handling of invalid inputs"""
        with self.assertRaises(ValueError):
            self.prover.add_clause([])  # Empty clause
            
        with self.assertRaises(ValueError):
            self.prover.prove("")  # Empty query

if __name__ == "__main__":
    unittest.main(verbosity=2)