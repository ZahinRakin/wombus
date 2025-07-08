# Wombus

## Description

Wombus is a Python-based implementation of the classic Wumpus World AI problem. It provides both a console-based and graphical interface for users to explore and solve the Wumpus World challenge. The game involves navigating a grid-based world, avoiding hazards like pits and the Wumpus, and collecting gold to achieve victory.

## Features

-   Console-based gameplay with text-based commands.
-   Graphical interface using Pygame for enhanced visuals.
-   Random world generation for replayability.
-   Customizable agent configuration.

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd wombus
    ```
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Console Mode

Run the game in console mode:

```bash
python wumpus.py
```

### Graphical Mode

To use the graphical interface, ensure Pygame is installed and run the graphical control script:

```bash
python graphical_control.py
```

### Random World Generation

Generate a random world configuration:

```bash
python generate_random_board.py
```

## Controls

-   `move <direction>`: Move the agent (up/down/left/right).
-   `grab`: Grab gold if present.
-   `shoot <direction>`: Shoot an arrow in the specified direction.
-   `status`: Display the current game status.
-   `help`: Show game instructions.
-   `reset`: Restart the game.
-   `quit`: Exit the game.

## Dependencies

-   Python 3.10 or higher
-   Pygame (install via `pip install pygame`)

## Files

-   `wumpus.py`: Main entry point for the console-based game.
-   `graphical_control.py`: Graphical interface for the game.
-   `generate_random_board.py`: Script to generate random world configurations.
-   `world_load.py`: Handles loading and managing the game world.
-   `agent.py`: Defines the agent and its behavior.
-   `game.py`: Core game logic.
-   `world.txt`: Default world configuration.
-   `board.txt`: Randomly generated world configuration.

## License

This project is licensed under the MIT License.
