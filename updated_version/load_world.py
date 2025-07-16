# import random
from typing import List, Tuple, Dict, Optional
from pathlib import Path

class WorldLoader:
    def __init__(self, file_path: str , world_size: Tuple[int, int] = (10, 10)):
        self.file_path = file_path
        self.world_size = world_size
        self.board: List[List[str]] = self.load_world()
        self.validate_world()

    def load_world(self) -> List[List[str]]:
        """Load world from file or generate default if not found"""
        try:
            with open(self.file_path, 'r') as file:
                return self._parse_world_file(file)
        except FileNotFoundError:
            print(f"World file '{self.file_path}' not found, generating default world")
            return self._generate_random_world()

    def _parse_world_file(self, file) -> List[List[str]]:
        """Parse world file into 2D array"""
        board = []
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip comments and empty lines
                board.append([c for c in line if c in ['W', 'P', 'G', '-', 'A']])
        
        # Validate dimensions
        if len(board) != self.world_size[0] or any(len(row) != self.world_size[1] for row in board):
            raise ValueError(f"World dimensions must be {self.world_size}")
        
        return board

    
    def _generate_random_world(self) -> List[List[str]]:
        """Generate a random world with specified elements"""
        import random
        board = [['-' for _ in range(self.world_size[1])] for _ in range(self.world_size[0])]
        
        # Randomly place gold, wumpus, and pits
        num_gold = random.randint(1, 3)
        num_wumpus = random.randint(1, 4)
        num_pits = random.randint(1, 4)
        
        for _ in range(num_gold):
            x, y = random.randint(0, self.world_size[0] - 1), random.randint(0, self.world_size[1] - 1)
            board[x][y] = 'G'
        
        for _ in range(num_wumpus):
            x, y = random.randint(0, self.world_size[0] - 1), random.randint(0, self.world_size[1] - 1)
            board[x][y] = 'W'
        
        for _ in range(num_pits):
            x, y = random.randint(0, self.world_size[0] - 1), random.randint(0, self.world_size[1] - 1)
            board[x][y] = 'P'
        
        return board

    def validate_world(self) -> None:
        """Validate world configuration"""
        if not any('G' in row for row in self.board):
            raise ValueError("World must contain at least one gold piece")
        

    def get_board(self) -> List[List[str]]:
        """Get a deep copy of the board"""
        return [row.copy() for row in self.board]

    def find_elements(self, element: str) -> List[Tuple[int, int]]:
        """Find all positions of a specific element"""
        return [
            (i, j) 
            for i, row in enumerate(self.board) 
            for j, val in enumerate(row) 
            if val == element
        ]

    def get_cell(self, row: int, col: int) -> Optional[str]:
        """Get cell content at position"""
        if 0 <= row < self.world_size[0] and 0 <= col < self.world_size[1]:
            return self.board[row][col]
        return None
    
    def set_cell(self, row: int, col: int, value: str) -> None:
        """Set cell content at position"""
        if 0 <= row < self.world_size[0] and 0 <= col < self.world_size[1]:
            self.board[row][col] = value
        else:
            raise IndexError("Cell position out of bounds")

    def print_world(self) -> None:
        """Print world layout"""
        print("\nWorld Layout:")
        print("  " + " ".join(str(i) for i in range(self.world_size[1])))
        for i, row in enumerate(self.board):
            print(f"{i} " + " ".join(row))


if __name__ == "__main__":
    loader = WorldLoader('world.txt', (10, 10))
    loader.print_world()
    print("Agent position:", loader.find_elements('A'))
    print("Gold positions:", loader.find_elements('G'))
    print("Wumpus positions:", loader.find_elements('W'))
    print("Pit positions:", loader.find_elements('P'))
