#!/bin/bash

# Root project folder
# mkdir -p wumpus_world_project
# cd wumpus_world_project || exit

# docs
# mkdir -p docs
touch docs/design_decisions.md
touch docs/user_manual.md

# src and subfolders
# mkdir -p src/agent src/environment src/interface src/game src/utils

touch src/agent/__init__.py
# touch src/agent/agent.py
touch src/agent/knowledge_base.py
touch src/agent/logic.py

touch src/environment/__init__.py
touch src/environment/world_load.py
touch src/environment/world_generator.py

touch src/interface/__init__.py
touch src/interface/graphical_control.py
touch src/interface/cli.py

touch src/game/__init__.py
# touch src/game/game.py
# touch src/game/wumpus.py

touch src/utils/__init__.py
touch src/utils/helpers.py
touch src/utils/constants.py

# tests and test_data
mkdir -p tests/test_data
touch tests/__init__.py
touch tests/test_agent.py
touch tests/test_knowledge.py
touch tests/test_world.py
touch tests/test_data/simple.world
touch tests/test_data/complex.world
touch tests/test_data/edge_cases.world

# worlds
# mkdir -p worlds
touch worlds/default.world
touch worlds/easy.world
touch worlds/hard.world

# Top-level files
# touch requirements.txt
# touch README.md
# touch .gitignore
