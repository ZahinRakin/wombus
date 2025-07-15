# import random
from typing import List, Tuple, Optional

class WorldLoader:
    def __init__(self, file_path: str = "worlds/default.world", world_size: Tuple[int, int] = (10, 10)):
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
            return self._generate_default_world()

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

    def _generate_default_world(self) -> List[List[str]]:
        """Generate a simple default world"""
        board = [['-' for _ in range(self.world_size[1])] for _ in range(self.world_size[0])]
        
        # Place agent
        board[9][0] = 'A'
        
        # Place some hazards and gold
        board[8][3] = 'P'
        board[8][6] = 'P'
        board[7][0] = 'P'
        board[7][7] = 'G'

        board[5][0] = 'W'
        board[5][6] = 'P'

        board[4][3] = 'G'

        board[3][5] = 'P'

        board[2][6] = 'P'

        board[1][2] = 'W'

        board[0][3] = 'P'
        board[0][6] = 'P'
        
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

    def print_world(self) -> None:
        """Print world layout"""
        print("\nWorld Layout:")
        print("  " + " ".join(str(i) for i in range(self.world_size[1])))
        for i, row in enumerate(self.board):
            print(f"{i} " + " ".join(row))