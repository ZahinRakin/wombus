import unittest
from collections import deque
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
        self.prover.add_clause(["¬W_1_1", "S_1_2"])
        self.prover.add_clause(["¬W_1_1", "S_2_1"])
        
        # We smell stench at (1,2) but not at (2,1)
        self.prover.add_clause(["S_1_2"])
        self.prover.add_clause(["¬S_2_1"])
        
        # Should infer Wumpus is at (1,1)
        self.assertTrue(self.prover.prove("W_1_1"))

    def test_safe_cell_inference(self):
        """Test safe cell deduction"""
        # If no stench, adjacent cells are safe
        self.prover.add_clause(["¬S_1_1", "W_1_0", "W_0_1", "W_2_1", "W_1_2"])
        self.prover.add_clause(["¬S_1_1"])  # No stench
        
        for pos in [(1,0), (0,1), (2,1), (1,2)]:
            self.assertTrue(self.prover.prove(f"¬W_{pos[0]}_{pos[1]}"))

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
        # Create an unsatisfiable KB that would run forever
        for i in range(100):
            self.prover.add_clause([f"X_{i}", f"Y_{i}"])
            self.prover.add_clause([f"¬X_{i}"])
            self.prover.add_clause([f"¬Y_{i}"])
        
        # Should return False rather than run forever
        self.assertFalse(self.prover.prove("Z", max_steps=50))

    # Negative Test Cases
    def test_unprovable_queries(self):
        """Test queries that shouldn't be provable"""
        self.prover.add_clause(["A", "B"])
        self.assertFalse(self.prover.prove("A"))
        self.assertFalse(self.prover.prove("B"))

    def test_invalid_input_handling(self):
        """Test handling of invalid inputs"""
        with self.assertRaises(Exception):
            self.prover.add_clause([])  # Empty clause
            
        with self.assertRaises(Exception):
            self.prover.prove("")  # Empty query

if __name__ == "__main__":
    unittest.main(verbosity=2)