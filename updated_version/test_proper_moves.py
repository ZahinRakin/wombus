#!/usr/bin/env python3
"""
Test sensing with proper move simulation
"""

from agent import Agent
from load_world import WorldLoader

def add_breeze_and_stench(world):
    """Add breeze and stench to world based on pits and wumpus"""
    temp_agent = Agent(world, position=(0, 0))
    
    for i in range(10):
        for j in range(10):
            neighbors = temp_agent.get_valid_neighbors(i, j)
            if world.get_cell(i, j) == 'P':
                for n in neighbors:
                    if world.get_cell(n[0], n[1]) == '-':
                        world.set_cell(n[0], n[1], 'B')
                    elif world.get_cell(n[0], n[1]) == 'S':
                        world.set_cell(n[0], n[1], 'BS')
            elif world.get_cell(i, j) == 'W':
                for n in neighbors:
                    if world.get_cell(n[0], n[1]) == '-':
                        world.set_cell(n[0], n[1], 'S')
                    elif world.get_cell(n[0], n[1]) == 'B':
                        world.set_cell(n[0], n[1], 'BS')

def test_sensing_with_moves():
    print("=== Testing Sensing with Proper Moves ===")
    
    # Load world and add breeze/stench
    world = WorldLoader('world.txt')
    add_breeze_and_stench(world)
    
    # Create agent at starting position
    agent = Agent(world, position=(9, 0), expected_gold=1)
    
    print(f"Starting at: {agent.current_position}")
    print(f"Initial sensing: {agent.get_sensing_info()}")
    
    # Test moving to position (8, 0) which should have breeze
    print(f"\n=== Testing Move to (8, 0) - Should have BREEZE ===")
    print(f"Cell at (8, 0): {world.get_cell(8, 0)}")
    
    # Move agent
    move_success = agent.move(8, 0)
    print(f"Move successful: {move_success}")
    print(f"Agent cell content: {agent.current_cell_content}")
    
    # Run AI_play to process sensing
    agent.AI_play()
    
    print(f"After AI_play:")
    print(f"  Current breeze: {agent.current_breeze}")
    print(f"  Current stench: {agent.current_stench}")
    print(f"  Sensing: {agent.get_sensing_info()}")
    print(f"  Events: {len(agent.recent_events)}")
    
    for event in agent.recent_events:
        print(f"  Event: {event['type']} - {event['message'].split('!')[0]}!")
    
    # Test moving to another sensing position
    print(f"\n=== Testing Move to (5, 1) - Should have STENCH ===")
    print(f"Cell at (5, 1): {world.get_cell(5, 1)}")
    
    # Reset sensing state for testing
    agent.last_sensing_state = {"breeze": False, "stench": False}
    agent.recent_events.clear()
    
    # Move agent
    move_success = agent.move(5, 1)
    print(f"Move successful: {move_success}")
    print(f"Agent cell content: {agent.current_cell_content}")
    
    # Run AI_play to process sensing
    agent.AI_play()
    
    print(f"After AI_play:")
    print(f"  Current breeze: {agent.current_breeze}")
    print(f"  Current stench: {agent.current_stench}")
    print(f"  Sensing: {agent.get_sensing_info()}")
    print(f"  Events: {len(agent.recent_events)}")
    
    for event in agent.recent_events:
        print(f"  Event: {event['type']} - {event['message'].split('!')[0]}!")
    
    print(f"\n✅ Sensing with proper moves test completed!")

if __name__ == "__main__":
    test_sensing_with_moves()
