#!/usr/bin/env python3
"""
Test breeze and stench popup events
"""

from agent import Agent
from load_world import WorldLoader

def add_breeze_and_stench(world):
    """Add breeze and stench to world based on pits and wumpus"""
    # Create a temporary agent to use the get_valid_neighbors method
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

def test_sensing_events():
    print("=== Testing Breeze and Stench Popup Events ===")
    
    # Load world and add breeze/stench
    world = WorldLoader('world.txt')
    add_breeze_and_stench(world)
    
    print("World after adding breeze and stench:")
    for i in range(10):
        for j in range(10):
            print(world.get_cell(i, j), end='')
        print()
    
    # Create agent
    agent = Agent(world, position=(9, 0), expected_gold=1)
    
    print(f"\nStarting at: {agent.current_position}")
    print(f"Initial sensing: {agent.get_sensing_info()}")
    
    # Find positions with breeze and stench
    breeze_positions = []
    stench_positions = []
    both_positions = []
    
    for i in range(10):
        for j in range(10):
            cell = world.get_cell(i, j)
            if cell == 'B':
                breeze_positions.append((i, j))
            elif cell == 'S':
                stench_positions.append((i, j))
            elif cell == 'BS':
                both_positions.append((i, j))
    
    print(f"Breeze positions: {breeze_positions[:3]}")  # Show first 3
    print(f"Stench positions: {stench_positions[:3]}")  # Show first 3  
    print(f"Both positions: {both_positions}")
    
    # Test breeze detection
    if breeze_positions:
        print(f"\n=== Testing Breeze Detection ===")
        pos = breeze_positions[0]
        agent.current_position = pos
        agent.last_sensing_state = {"breeze": False, "stench": False}
        agent.recent_events.clear()
        
        print(f"Moving to breeze position: {pos}")
        agent.AI_play()
        
        print(f"Current breeze: {agent.current_breeze}")
        print(f"Sensing: {agent.get_sensing_info()}")
        print(f"Events: {len(agent.recent_events)}")
        for event in agent.recent_events:
            print(f"  -> {event['type']}: {event['message'].split('!')[0]}!")
    
    # Test stench detection
    if stench_positions:
        print(f"\n=== Testing Stench Detection ===")
        pos = stench_positions[0]
        agent.current_position = pos
        agent.last_sensing_state = {"breeze": False, "stench": False}
        agent.recent_events.clear()
        
        print(f"Moving to stench position: {pos}")
        agent.AI_play()
        
        print(f"Current stench: {agent.current_stench}")
        print(f"Sensing: {agent.get_sensing_info()}")
        print(f"Events: {len(agent.recent_events)}")
        for event in agent.recent_events:
            print(f"  -> {event['type']}: {event['message'].split('!')[0]}!")
    
    # Test both breeze and stench
    if both_positions:
        print(f"\n=== Testing Both Breeze and Stench ===")
        pos = both_positions[0]
        agent.current_position = pos
        agent.last_sensing_state = {"breeze": False, "stench": False}
        agent.recent_events.clear()
        
        print(f"Moving to both position: {pos}")
        agent.AI_play()
        
        print(f"Current breeze: {agent.current_breeze}")
        print(f"Current stench: {agent.current_stench}")
        print(f"Sensing: {agent.get_sensing_info()}")
        print(f"Events: {len(agent.recent_events)}")
        for event in agent.recent_events:
            print(f"  -> {event['type']}: {event['message'].split('!')[0]}!")
    
    print(f"\n✅ Sensing event test completed!")

if __name__ == "__main__":
    test_sensing_events()
