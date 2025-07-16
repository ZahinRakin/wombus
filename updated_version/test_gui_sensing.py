#!/usr/bin/env python3
"""
Test GUI sensing display
"""

import tkinter as tk
from gui_improved import WumpusWorldGUI
import time

def test_gui_sensing():
    print("=== Testing GUI Sensing Display ===")
    
    # Create GUI
    app = WumpusWorldGUI()
    
    # Load world
    app.start_game('world.txt')
    
    print("World loaded, breeze and stench added")
    
    # Check if agent has sensing methods
    if hasattr(app.agent, 'get_sensing_info'):
        print(f"Agent sensing info method: AVAILABLE")
    else:
        print(f"Agent sensing info method: MISSING")
    
    # Check current sensing at starting position
    initial_sensing = app.agent.get_sensing_info()
    print(f"Initial sensing at {app.agent.current_position}: {initial_sensing}")
    
    # Manually move agent to a position with breeze/stench
    # Find a position with breeze or stench
    breeze_pos = None
    stench_pos = None
    
    for i in range(10):
        for j in range(10):
            cell = app.world.get_cell(i, j)
            if cell == 'B' and not breeze_pos:
                breeze_pos = (i, j)
            elif cell == 'S' and not stench_pos:
                stench_pos = (i, j)
    
    print(f"Found breeze at: {breeze_pos}")
    print(f"Found stench at: {stench_pos}")
    
    if breeze_pos:
        print(f"\n--- Testing Breeze Position {breeze_pos} ---")
        app.agent.current_position = breeze_pos
        app.agent.AI_play()
        sensing = app.agent.get_sensing_info()
        print(f"Sensing after AI_play: {sensing}")
        print(f"Current breeze: {app.agent.current_breeze}")
        print(f"Current stench: {app.agent.current_stench}")
        
        # Update GUI labels manually
        if hasattr(app, 'sensing_label'):
            app.sensing_label.config(text=sensing)
            print(f"GUI sensing label updated to: {sensing}")
        else:
            print("GUI sensing label not found!")
    
    # Don't start the GUI mainloop, just exit
    print("✅ GUI sensing test completed")

if __name__ == "__main__":
    test_gui_sensing()
