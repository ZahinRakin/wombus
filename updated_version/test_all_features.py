#!/usr/bin/env python3
"""
Test script to demonstrate all implemented features
"""

from agent import Agent
from load_world import WorldLoader

def test_scoring_system():
    """Test the scoring system"""
    print("=== Testing Scoring System ===")
    
    # Load a world
    world = WorldLoader('easy.txt')
    agent = Agent(world, position=(9, 0), expected_gold=1)
    
    print(f"Initial score: {agent.score}")
    print(f"Initial position: {agent.current_position}")
    
    # Test movement (should decrease score by 1)
    agent.AI_play()
    print(f"After AI_play() - Score: {agent.score}")
    
    # Test sensing
    sensing_info = agent.get_sensing_info()
    print(f"Sensing information: {sensing_info}")
    
    return agent

def test_sensing_detection():
    """Test sensing detection"""
    print("\n=== Testing Sensing Detection ===")
    
    # Create agent and test different positions
    world = WorldLoader('easy.txt')
    agent = Agent(world, position=(9, 0), expected_gold=1)
    
    # Test at starting position
    print(f"Position {agent.current_position}: {agent.get_sensing_info()}")
    
    # Manually set position to test breeze/stench detection
    test_positions = [(8, 0), (7, 0), (6, 0), (5, 0)]
    
    for pos in test_positions:
        agent.current_position = pos
        sensing = agent.get_sensing_info()
        print(f"Position {pos}: {sensing}")

def main():
    """Main test function"""
    print("Testing Wumpus World Enhanced Features")
    print("=====================================")
    
    # Test scoring
    agent = test_scoring_system()
    
    # Test sensing
    test_sensing_detection()
    
    print("\n=== Score Breakdown ===")
    print("Initial score: 0")
    print("Each step: -1 point")
    print("Gold found: +1000 points")
    print("Winning (returning to start): +500 points")
    print("Death: -1000 points")
    
    print("\n=== How to Run GUIs ===")
    print("Basic GUI: python3 run_improved_gui.py")
    print("Debug GUI: python3 debug_gui.py")
    print("\nThe debug GUI shows:")
    print("- Real-time score updates")
    print("- Current sensing information (breeze/stench)")
    print("- Agent's knowledge base")
    print("- Move history and pathfinding")
    print("- Detailed game statistics")

if __name__ == "__main__":
    main()
