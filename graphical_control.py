import pygame # type: ignore
import time

TILE_SIZE = 50
ROWS, COLS = 10, 10
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE

COLORS = {
    '-': (220, 220, 220),
    'P': (0, 100, 255),
    'W': (139, 0, 0),
    'G': (255, 215, 0),
    'X': (0, 0, 0),  # dead
    'V': (0, 255, 0)  # victory
}

class WumpusGame:
    def __init__(self, board_file='board.txt'):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Wumpus Game")

        self.board = self.load_board(board_file)
        self.player_pos = (9, 0)

    def load_board(self, filename):
        with open(filename) as f:
            return [list(line.strip()) for line in f.readlines()]

    def find_player(self):
        for y in range(ROWS):
            for x in range(COLS):
                if self.board[y][x] == 'P':
                    return (x, y)
        return None

    def draw_board(self):
        for y in range(ROWS):
            for x in range(COLS):
                tile = self.board[y][x]
                pygame.draw.rect(
                    self.screen,
                    COLORS.get(tile, (255, 255, 255)),
                    (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                )
                pygame.draw.rect(self.screen, (0, 0, 0), (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
        pygame.display.flip()

    def move(self, dx, dy):
        x, y = self.player_pos
        nx, ny = x + dx, y + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS:
            self.board[y][x] = '-'
            self.player_pos = (nx, ny)
            self.board[ny][nx] = 'P'
            self.draw_board()
            time.sleep(0.2)

    def move_up(self): self.move(0, -1)
    def move_down(self): self.move(0, 1)
    def move_left(self): self.move(-1, 0)
    def move_right(self): self.move(1, 0)

    def die(self):
        x, y = self.player_pos
        self.board[y][x] = 'X'
        self.draw_board()
        time.sleep(0.5)

    def grab_gold(self):
        x, y = self.player_pos
        if self.board[y][x] == 'G':
            self.board[y][x] = 'P'
        self.draw_board()
        time.sleep(0.5)

    def fall_into_pit(self):
        x, y = self.player_pos
        self.board[y][x] = 'X'
        self.draw_board()
        time.sleep(0.5)

    def victory(self):
        x, y = self.player_pos
        self.board[y][x] = 'V'
        self.draw_board()
        time.sleep(0.5)

    def run(self):
        running = True
        self.draw_board()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        pygame.quit()


def main():
    # Create an instance and control the game
    game = WumpusGame('board.txt')
    game.draw_board()

    # Perform actions
    game.move_right()
    game.move_down()
    game.grab_gold()
    game.victory()


if __name__ == "__main__":
    main()