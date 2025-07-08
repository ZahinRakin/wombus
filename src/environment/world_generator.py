import random
from typing import List, Tuple
from pathlib import Path

class WorldGenerator:
    def __init__(self, world_size: Tuple[int, int] = (10, 10)):
        self.world_size = world_size
        self.min_pits = 3
        self.max_pits = 8
        self.gold_count = 1
        self.wumpus_count = 1

    def generate_random_world(self, filename: str = None) -> List[List[str]]:
        """Generate a random valid world"""
        while True:
            try:
                board = self._create_empty_world()
                self._place_agent(board)
                self._place_gold(board)
                self._place_wumpus(board)
                self._place_pits(board)
                
                if filename:
                    self._save_world(board, filename)
                
                return board
            except ValueError:
                continue  # Retry if placement was invalid

    def _create_empty_world(self) -> List[List[str]]:
        """Create empty world grid"""
        return [['-' for _ in range(self.world_size[1])] 
                for _ in range(self.world_size[0])]

    def _place_agent(self, board: List[List[str]]) -> None:
        """Place agent at starting position"""
        board[-1][0] = 'A'  # Bottom-left corner

    def _place_gold(self, board: List[List[str]]) -> None:
        """Place gold in a random safe location"""
        for _ in range(self.gold_count):
            while True:
                x, y = random.randint(0, self.world_size[0]-1), random.randint(0, self.world_size[1]-1)
                if board[x][y] == '-' and (x, y) != (self.world_size[0]-1, 0):
                    board[x][y] = 'G'
                    break

    def _place_wumpus(self, board: List[List[str]]) -> None:
        """Place Wumpus ensuring it's not next to agent"""
        for _ in range(self.wumpus_count):
            while True:
                x, y = random.randint(0, self.world_size[0]-1), random.randint(0, self.world_size[1]-1)
                # Ensure Wumpus isn't adjacent to starting position
                if (board[x][y] == '-' and 
                    abs(x - (self.world_size[0]-1)) + abs(y - 0) > 1):
                    board[x][y] = 'W'
                    break

    def _place_pits(self, board: List[List[str]]) -> None:
        """Place pits randomly while ensuring solvability"""
        pit_count = random.randint(self.min_pits, self.max_pits)
        placed = 0
        
        while placed < pit_count:
            x, y = random.randint(0, self.world_size[0]-1), random.randint(0, self.world_size[1]-1)
            if board[x][y] == '-' and (x, y) != (self.world_size[0]-1, 0):
                board[x][y] = 'P'
                placed += 1

    def _save_world(self, board: List[List[str]], filename: str) -> None:
        """Save world to file"""
        # Ensure worlds directory exists
        Path("worlds").mkdir(exist_ok=True)
        
        with open(f"worlds/{filename}", 'w') as f:
            f.write("# Generated Wumpus World\n")
            f.write("# Format: W=Wumpus, P=Pit, G=Gold, -=Empty, A=Agent\n")
            for row in board:
                f.write("".join(row) + "\n")

    @staticmethod
    def generate_sample_worlds() -> None:
        """Generate sample world configurations"""
        generator = WorldGenerator()
        
        # Easy world
        easy_world = generator.generate_random_world("easy.world")
        generator._save_world(easy_world, "easy.world")
        
        # Medium world
        generator.min_pits = 5
        generator.max_pits = 10
        medium_world = generator.generate_random_world("medium.world")
        generator._save_world(medium_world, "medium.world")
        
        # Hard world
        generator.min_pits = 8
        generator.max_pits = 15
        generator.wumpus_count = 1  # Still only one Wumpus
        hard_world = generator.generate_random_world("hard.world")
        generator._save_world(hard_world, "hard.world")

if __name__ == "__main__":
    # Generate sample worlds when run directly
    WorldGenerator.generate_sample_worlds()