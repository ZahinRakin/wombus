#!/usr/bin/env python3
"""
Wumpus World Game with GUI
Run this file to start the graphical version of the Wumpus World game.
"""

from gui import WumpusWorldGUI

if __name__ == "__main__":
    print("Starting Wumpus World GUI...")
    app = WumpusWorldGUI()
    app.run()
