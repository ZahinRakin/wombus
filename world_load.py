class WorldBuilder:
    def __init__(self, file_path=None, starting_point=(0, 0)):
        self.board = self.build(file_path, starting_point)
        

    def build(self, file_path, starting_point):
        try:
            with open(file_path, 'r') as file:
                board_str = file.read()

                rows = board_str.strip().split('\n')

                board = [[i for i in row] for row in rows]

                if (len(board), len(board[1])) != (10, 10):
                    raise ValueError("Board must be of shape (10, 10)")

                board[starting_point[0]][starting_point[1]] = 'A'

            return board
        
        except Exception as e:
            print(f"An unexpected error occurred when reading the file!!")

    def print_board(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                print(self.board[i][j], end=' ')
            print()
    
world = WorldBuilder(file_path='world.txt', starting_point=(9, 0))
world.print_board()
