# Wombus
## Description

Wombus is a Python-based implementation of the classic Wumpus World AI problem. It provides both a console-based and graphical interface for users to explore and solve the Wumpus World challenge. The game involves navigating a grid-based world, avoiding hazards like pits and the Wumpus, and collecting gold to achieve victory.

## Features

-   Console-based gameplay with text-based commands.
-   Graphical interface using Pygame for enhanced visuals.
-   Random world generation for replayability.
-   Customizable agent configuration.
-   AI-driven agent with logical reasoning using propositional logic and resolution.

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
python -m src.interface.cli
```

### Graphical Mode

To use the graphical interface, ensure Pygame is installed and run the graphical control script:

```bash
python -m src.game.wumpus
```

### Random World Generation

Generate a random world configuration:

```bash
python -m src.environment.world_generator
```

### Running Tests

Run all tests to ensure the project is functioning correctly:

```bash
python -m pytest tests/
```

## Controls

-   `move <direction>`: Move the agent (up/down/left/right).
-   `shoot <direction>`: Shoot an arrow in the specified direction.
-   `grab`: Grab gold if present.
-   `status`: Display the current game status.
-   `restart`: Restart the game.
-   `quit`: Exit the game.

## Dependencies

-   Python 3.10 or higher
-   Pygame (install via `pip install pygame`)

## Files

### Source Code
-   `src/agent/agent.py`: Defines the agent and its behavior.
-   `src/agent/knowledge_base.py`: Manages the agent's knowledge and logical reasoning.
-   `src/agent/logic.py`: Implements the resolution prover and propositional logic.
-   `src/environment/world_load.py`: Handles loading and managing the game world.
-   `src/environment/world_generator.py`: Generates random worlds.
-   `src/game/game.py`: Core game logic.
-   `src/game/wumpus.py`: Entry point for running the game.
-   `src/interface/cli.py`: Command-line interface for the game.
-   `src/interface/graphical_control.py`: Graphical interface for the game.
-   `src/utils/helpers.py`: Utility functions for the project.
-   `src/utils/constants.py`: Constants used throughout the project.

### Worlds
-   `worlds/default.world`: Default world configuration.
-   `worlds/easy.world`: Predefined easy difficulty world.
-   `worlds/medium.world`: Predefined medium difficulty world.
-   `worlds/hard.world`: Predefined hard difficulty world.

### Tests
-   `tests/test_agent.py`: Tests for the agent's behavior.
-   `tests/test_resolution_prover.py`: Tests for the resolution prover.
-   `tests/test_world.py`: Tests for world-related functionality.
-   `tests/test_knowledge.py`: Tests for the knowledge base.

## License

This project is licensed under the MIT License.
