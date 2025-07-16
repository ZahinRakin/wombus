# Wumpus World Game with GUI

This is a graphical implementation of the classic Wumpus World AI game using Python and tkinter.

## Features

- **Dual View Interface**: Side-by-side comparison of agent's knowledge vs complete world
- **Enhanced Symbols**: Clear text-based symbols for all game elements
- **Multiple Difficulty Levels**: Easy, Medium, Hard, and Random worlds
- **Custom World Files**: Load your own world configurations
- **Real-time Visualization**: Watch the agent explore and collect gold
- **Game Legend**: Clear symbols and color coding for all elements
- **Game Status**: Track gold collection and game progress
- **Two GUI Versions**: Basic (with simple symbols) and Enhanced (with descriptive text)

## How to Run

### Option 1: Run the Enhanced GUI version (Recommended)
```bash
python3 run_improved_gui.py
```

### Option 2: Run the Debug version (for troubleshooting)
```bash
python3 debug_gui.py
```
**Features:**
- Real-time debug information panels
- Agent status display (position, gold, path, neighbors)
- Knowledge base visualization
- Move history and path tracking
- Invalid move detection and prevention
- Step-by-step console logging

### Option 3: Run the Basic GUI version
```bash
python3 run_gui.py
```

### Option 4: Run the original console version
```bash
python3 main.py
```

## How to Play

1. **Start the Game**: Run `python3 run_improved_gui.py` for the best experience
2. **Select World**: Choose from Easy, Medium, Hard, Random, or load a custom file
3. **Observe Dual Views**: 
   - Left panel shows agent's current knowledge (explored areas only)
   - Right panel shows the complete world layout (god's view)
4. **Start Game**: Click the "Start Game" button to begin the simulation
5. **Watch**: The agent will automatically explore the world and collect gold
6. **Reset**: Use the "Reset" button to restart the current world

## Game Elements

### Enhanced GUI Version
| Symbol | Element | Description |
|--------|---------|-------------|
| AGENT | Agent | The AI player (green background) |
| GOLD | Gold | Treasure to collect (gold background) |
| WUMPUS | Wumpus | Dangerous creature (red background) |
| PIT | Pit | Deadly trap (black background) |
| BREEZE | Breeze | Indicates nearby pit (light blue background) |
| STENCH | Stench | Indicates nearby wumpus (pink background) |
| VISIT | Visited | Previously explored cell (gray background) |

### Basic GUI Version
| Symbol | Element | Description |
|--------|---------|-------------|
| A | Agent | The AI player |
| G | Gold | Treasure to collect |
| W | Wumpus | Dangerous creature |
| P | Pit | Deadly trap |
| B | Breeze | Indicates nearby pit |
| S | Stench | Indicates nearby wumpus |
| + | Visited | Previously explored cell |

## World File Format

Create custom worlds using text files with the following format:
- `A`: Agent starting position (must be at position 9,0)
- `G`: Gold
- `W`: Wumpus
- `P`: Pit
- `-`: Empty cell

Example (10x10 grid):
```
----------
----------
---P------
------W---
G---------
----------
----------
----------
----------
A--------G
```

## Game Logic

- The agent starts at position (9,0)
- Breezes appear adjacent to pits
- Stenches appear adjacent to wumpuses
- The agent uses logical reasoning to avoid dangers
- Goal: Collect all gold and return safely
- **Game End Conditions**:
  - **Victory**: All expected gold is collected
  - **Victory with Return**: All gold collected AND agent returns to starting position
  - **Game Over**: No safe moves available (agent is trapped)
  - **Maximum Steps**: Game stops after 1000 steps (indicates potential infinite loop)

## Recent Fixes

- **Fixed Invalid Move Bug**: Prevented agent from getting stuck trying to move to its current position
- **Enhanced Move Validation**: Added checks to ensure all moves are valid and adjacent
- **Fixed Step Limit Issue**: Increased from 100 to 1000 steps to allow proper exploration
- **Improved Agent Logic**: Better pathfinding and backtracking mechanisms
- **Enhanced Goal Detection**: Game only ends when objectives are truly met
- **Added Comprehensive Debug Mode**: Real-time display of agent's internal state
  - Agent position, gold count, and available moves
  - Knowledge base summary and safe/dangerous cell tracking
  - Path history and move validation
  - Error detection and prevention

## Files

- `run_improved_gui.py`: Enhanced launcher with dual-view and clear symbols
- `run_gui.py`: Basic launcher for GUI version
- `gui_improved.py`: Enhanced GUI implementation with text symbols
- `gui.py`: Basic GUI implementation using tkinter
- `agent.py`: AI agent logic
- `load_world.py`: World loading and management
- `main.py`: Original console version
- `easy.txt`, `medium.txt`, `hard.txt`: Predefined worlds

## Requirements

- Python 3.x
- tkinter (usually included with Python)
- No additional packages required!
