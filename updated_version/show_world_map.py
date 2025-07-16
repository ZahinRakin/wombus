#!/usr/bin/env python3
"""
Show the world map with breeze and stench after loading
"""

from load_world import WorldLoader
from agent import Agent

def show_world_with_sensing():
    print("=== World Map with Breeze and Stench ===")
    
    # Load world
    world = WorldLoader('world.txt')
    
    print("Original world:")
    for i in range(10):
        for j in range(10):
            print(world.get_cell(i, j), end='')
        print()
    
    # Add breeze and stench like the GUI does
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
    
    print("\nWorld with breeze (B) and stench (S):")
    for i in range(10):
        for j in range(10):
            cell = world.get_cell(i, j)
            print(cell, end='')
        print()
    
    # Show agent's starting path and what it should encounter
    print(f"\nAgent starts at (9, 0): {world.get_cell(9, 0)}")
    print(f"Next position (8, 0): {world.get_cell(8, 0)}")
    print(f"Next position (8, 1): {world.get_cell(8, 1)}")
    print(f"Next position (7, 1): {world.get_cell(7, 1)}")
    print(f"Next position (6, 1): {world.get_cell(6, 1)}")
    print(f"Next position (5, 1): {world.get_cell(5, 1)}")
    
    # Look for nearby breeze/stench positions on the likely path
    likely_path = [(9,0), (8,0), (8,1), (7,1), (6,1), (5,1), (4,1), (3,1), (2,1), (1,1), (0,1)]
    for pos in likely_path:
        i, j = pos
        if i < 10 and j < 10:
            cell = world.get_cell(i, j)
            if cell in ['B', 'S', 'BS']:
                print(f"🎯 SENSING at {pos}: {cell}")

if __name__ == "__main__":
    show_world_with_sensing()
