import random
import math
from typing import List, Tuple, Dict, Set, Optional
from pathlib import Path
from .constants import *

def calculate_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """Calculate Euclidean distance between two positions"""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def get_adjacent_positions(position: Tuple[int, int], 
                          world_size: Tuple[int, int] = WORLD_SIZE) -> List[Tuple[int, int]]:
    """Get valid adjacent positions (up, down, left, right)"""
    x, y = position
    adjacent = [
        (x-1, y), (x+1, y),
        (x, y-1), (x, y+1)
    ]
    return [
        (i, j) for i, j in adjacent 
        if 0 <= i < world_size[0] and 0 <= j < world_size[1]
    ]

def direction_to_move(current: Tuple[int, int], target: Tuple[int, int]) -> Optional[str]:
    """Determine best direction to move from current to target position"""
    dx = target[0] - current[0]
    dy = target[1] - current[1]
    
    if abs(dx) > abs(dy):
        return 'down' if dx > 0 else 'up'
    elif dy != 0:
        return 'right' if dy > 0 else 'left'
    return None

def generate_unique_positions(count: int, 
                            world_size: Tuple[int, int] = WORLD_SIZE,
                            exclude: List[Tuple[int, int]] = None) -> Set[Tuple[int, int]]:
    """Generate unique random positions excluding certain positions"""
    exclude = exclude or []
    positions = set()
    
    while len(positions) < count:
        pos = (random.randint(0, world_size[0]-1), random.randint(0, world_size[1]-1))
        if pos not in exclude and pos not in positions:
            positions.add(pos)
    
    return positions

def load_world_file(file_path: str) -> List[List[str]]:
    """Load world from file with validation"""
    path = Path("worlds") / file_path if not file_path.startswith("worlds/") else Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"World file {path} not found")
    
    with open(path, 'r') as f:
        world = []
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                world.append([c for c in line if c in SYMBOLS.values()])
    
    # Validate world size
    if len(world) != WORLD_SIZE[0] or any(len(row) != WORLD_SIZE[1] for row in world):
        raise ValueError(f"World must be {WORLD_SIZE} cells")
    
    return world

def save_world_file(world: List[List[str]], file_name: str) -> None:
    """Save world to file"""
    path = Path("worlds") / file_name
    path.parent.mkdir(exist_ok=True)
    
    with open(path, 'w') as f:
        f.write("# Wumpus World Configuration\n")
        f.write("# Symbols: A=Agent, W=Wumpus, P=Pit, G=Gold, -=Empty\n")
        for row in world:
            f.write("".join(row) + "\n")

def get_percepts(world: List[List[str]], position: Tuple[int, int]) -> List[str]:
    """Get percepts at given position"""
    percepts = []
    x, y = position
    
    # Check current cell first
    if world[x][y] == SYMBOLS['gold']:
        percepts.append(PERCEPTS['glitter'])
    
    # Check adjacent cells
    for i, j in get_adjacent_positions(position):
        if world[i][j] == SYMBOLS['wumpus'] and PERCEPTS['stench'] not in percepts:
            percepts.append(PERCEPTS['stench'])
        elif world[i][j] == SYMBOLS['pit'] and PERCEPTS['breeze'] not in percepts:
            percepts.append(PERCEPTS['breeze'])
    
    return percepts if percepts else [PERCEPTS['nothing']]

def validate_world(world: List[List[str]]) -> bool:
    """Validate world configuration"""
    # Check for exactly one agent start position
    agent_positions = sum(row.count(SYMBOLS['agent']) for row in world)
    if agent_positions != 1:
        raise ValueError("World must have exactly one agent starting position")
    
    # Check for at least one gold
    if not any(SYMBOLS['gold'] in row for row in world):
        raise ValueError("World must contain at least one gold")
    
    # Check for at most one Wumpus
    if sum(row.count(SYMBOLS['wumpus']) for row in world) > 1:
        raise ValueError("World can have at most one Wumpus")
    
    return True

def calculate_score(actions: List[str], 
                   has_gold: bool, 
                   wumpus_killed: bool,
                   difficulty: str = 'medium') -> int:
    """Calculate score based on game outcomes"""
    base_score = 0
    cost_map = {
        'move': SCORING['move_cost'],
        'shoot': SCORING['arrow_cost']
    }
    
    # Deduct action costs
    for action in actions:
        base_score -= cost_map.get(action, 0)
    
    # Add rewards
    if has_gold:
        base_score += SCORING['gold_reward']
    if wumpus_killed:
        base_score += SCORING['wumpus_kill_bonus']
    
    # Apply difficulty multiplier
    difficulty_factor = {'easy': 1.0, 'medium': 1.2, 'hard': 1.5}[difficulty]
    return int(base_score * difficulty_factor)