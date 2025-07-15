from typing import Dict, Tuple, List

# Game constants
WORLD_SIZE: Tuple[int, int] = (10, 10)
AGENT_START_POS: Tuple[int, int] = (9, 0)

# Symbols for world elements
SYMBOLS: Dict[str, str] = {
    'agent': 'A',
    'wumpus': 'W',
    'pit': 'P',
    'gold': 'G',
    'empty': '-',
    'visited': '.'
}

# Scoring constants
SCORING: Dict[str, int] = {
    'move_cost': 1,
    'arrow_cost': 10,
    'gold_reward': 1000,
    'death_penalty': 1000,
    'win_bonus': 500,
    'wumpus_kill_bonus': 500
}

# Difficulty settings
DIFFICULTY: Dict[str, Dict] = {
    'easy': {
        'pits': (3, 5),
        'arrows': 3,
        'penalty': 1000
    },
    'medium': {
        'pits': (5, 8),
        'arrows': 2,
        'penalty': 1500
    },
    'hard': {
        'pits': (7, 10),
        'arrows': 1,
        'penalty': 2000
    }
}

# Movement directions
DIRECTIONS: Dict[str, Tuple[int, int]] = {
    'up': (-1, 0),
    'down': (1, 0),
    'left': (0, -1),
    'right': (0, 1)
}

# Percept messages
PERCEPTS: Dict[str, str] = {
    'stench': "Stench",
    'breeze': "Breeze",
    'glitter': "Glitter",
    'bump': "Bump",
    'scream': "Scream",
    'nothing': "Nothing"
}

# Game messages
MESSAGES: Dict[str, str] = {
    'win': "🎉 You won!",
    'pit_death': "💀 Fell into a pit!",
    'wumpus_death': "💀 Eaten by Wumpus!",
    'arrow_miss': "🏹 Arrow missed!",
    'wumpus_kill': "🏹 Wumpus killed!",
    'gold_grab': "✨ Gold collected!",
    'invalid_move': "Can't move that way!"
}

# Knowledge base constants
KB_CONSTANTS: Dict[str, str] = {
    'wumpus': 'W',
    'pit': 'P',
    'safe': 'S',
    'possible_wumpus': 'W?',
    'possible_pit': 'P?'
}

# the below constant is actually in use in game.py
percepts = [["" for _ in range(10)] for _ in range(10)]  # 10x10 grid for percepts