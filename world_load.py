class WorldBuilder:
    def __init__(self, file_path=None, starting_point=None):
        self.board = self.build(file_path) if file_path else None
        self.starting_point = starting_point
        

    def build(self, file_path):
        with open(file_path, 'r') as file:
            board_str = file.read()

            rows = board_str.strip().split('\n')

            board = [[i for i in row] for row in rows]

            print(len(board), len(board[1]))

            if (len(board), len(board[1])) != (10, 10):
                raise ValueError("Board must be of shape (10, 10)")

        return board
    
    def assign_agent(self):
        pass
        
world = WorldBuilder(file_path='world.txt', starting_point=(0, 0))
print(world.board)