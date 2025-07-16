#!/usr/bin/env python3
"""
Launcher for the enhanced Wumpus World GUI with scoring and sensing display
"""

if __name__ == "__main__":
    print("Starting Enhanced Wumpus World GUI...")
    print("Features:")
    print("- Real-time score display")
    print("- Sensing information (breeze/stench detection)")
    print("- Dual-view layout (agent's view + complete world)")
    print("- Speed controls")
    print("- Debug information")
    print()
    
    from gui_improved import WumpusWorldGUI
    app = WumpusWorldGUI()
    app.run()
