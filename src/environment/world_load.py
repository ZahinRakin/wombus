import random


class WorldLoader:
    
    def __init__(self, file_path = "world.txt", world_size=(10, 10)):
        self.file_path = file_path
        self.world_size = world_size
        self.board = self.load_world()

    def generate_random_board(self, filename='board.txt'):
        rows, cols = 10, 10
        chars = ['W', 'G', '-', 'P']
        board = [['-' for _ in range(10)] for _ in range(10)]
        gold_appeared = False
        
        board[9][0] = 'A' # I should be able to change the player position.
        
        for i in range(rows):
            # row = ['-'] * cols
            num_items = random.randint(0, 4)  # place 1 to 4 items per row
            for j in range(num_items):
                if not gold_appeared:
                    char = random.choice(['P', 'W', 'G'])
                else:
                    char = random.choice(['P', 'W'])
                pos = random.randint(0, cols - 1)
                if board[i][pos] == '-':
                    board[i][pos] = char
                    if char == 'G':
                        gold_appeared = True

        with open(filename, 'w') as f:
            for row in board:
                f.write(''.join(row) + '\n')
    

    def load_world(self):
        try:
            with open(self.file_path, 'r') as file:
                board_str = file.read()
                rows = board_str.strip().split('\n')
                board = [[char for char in row] for row in rows]
                
                if (len(board), len(board[0])) != self.world_size:
                    raise ValueError(f"Board must be of shape {self.world_size}")
                
                return board
        except FileNotFoundError:
            print(f"Error: File '{self.file_path}' not found!")
            return None
        except Exception as e:
            print(f"An unexpected error occurred when reading the file: {e}")
            return None

        
    # Get a copy of the board
    def get_board(self):
        if self.board:
            return [row[:] for row in self.board] # i am getting error here why
        return self.load_world()
    
    def get_cell(self, row, col):
        if self.board and 0 <= row < len(self.board) and 0 <= col < len(self.board[0]):
            return self.board[row][col]
        return None
    
    # Find all positions of a specific element in the world
    def find_elements(self, element):
        positions = []
        if self.board:
            for i in range(len(self.board)):
                for j in range(len(self.board[i])):
                    if self.board[i][j] == element:
                        positions.append((i, j))
        return positions
    
    def print_world(self):
        if self.board:
            print("\nOriginal World Layout:")
            print("  " + " ".join([str(i) for i in range(len(self.board[0]))]))
            for i in range(len(self.board)):
                print(f"{i} ", end="")
                for j in range(len(self.board[i])):
                    print(self.board[i][j], end=' ')
                print()
        else:
            print("No world loaded!")

# for checking is everything ok?
if __name__ == "__main__":
    world = WorldLoader('world.txt')
    world.print_world()
    print(f"Wumpus positions: {world.find_elements('W')}")
    print(f"Pit positions: {world.find_elements('P')}")
    print(f"Gold positions: {world.find_elements('G')}")
