import random

def generate_random_board(filename='board.txt'):
    rows, cols = 10, 10
    chars = ['P', 'W', 'G', '-']
    board = []

    for _ in range(rows):
        row = ['-'] * cols
        num_items = random.randint(1, 4)  # place 1 to 4 items per row
        for _ in range(num_items):
            char = random.choice(['P', 'W', 'G'])
            pos = random.randint(0, cols - 1)
            row[pos] = char
        board.append(''.join(row))

    with open(filename, 'w') as f:
        f.write('\n'.join(board))


if __name__ == "__main__":
    generate_random_board()