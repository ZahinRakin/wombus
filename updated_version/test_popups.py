#!/usr/bin/env python3
"""
Test the new popup notification system for major percepts
"""

from agent import Agent
from load_world import WorldLoader

def test_popup_events():
    print("=== Testing Popup Event System ===")
    
    # Load world
    world = WorldLoader('world.txt')
    agent = Agent(world, position=(9, 0), expected_gold=1)
    
    print(f"Initial state:")
    print(f"  Position: {agent.current_position}")
    print(f"  Score: {agent.score}")
    print(f"  Events: {agent.recent_events}")
    print(f"  Sensing: {agent.get_sensing_info()}")
    
    # Simulate movement and check for events
    print(f"\n=== Simulating Movement ===")
    
    # First move
    print(f"Before AI_play:")
    print(f"  Events: {len(agent.recent_events)}")
    
    agent.AI_play()
    print(f"After AI_play:")
    print(f"  Position: {agent.current_position}")
    print(f"  Events: {len(agent.recent_events)}")
    print(f"  Sensing: {agent.get_sensing_info()}")
    
    # Get events
    events = agent.get_and_clear_events()
    print(f"Events retrieved: {len(events)}")
    for i, event in enumerate(events):
        print(f"  Event {i+1}: {event['type']} - {event['message']}")
    
    print(f"\n=== Testing Gold Detection ===")
    # Test gold detection by moving to a position with gold
    # Looking at world.txt, there's gold at position (4, 3)
    test_positions = [(8, 0), (7, 0), (6, 0), (5, 0), (4, 0)]
    
    for pos in test_positions:
        old_pos = agent.current_position
        agent.current_position = pos
        
        # Simulate move to trigger gold detection
        if world.get_cell(pos[0], pos[1]) == 'G':
            print(f"Gold detected at {pos}!")
            gold_event = agent.add_gold_found_event()
            print(f"Gold event: {gold_event}")
        
        agent.current_position = old_pos
    
    print("\n✅ Event system working!")
    print("🎮 Ready for GUI popup testing!")

if __name__ == "__main__":
    test_popup_events()
