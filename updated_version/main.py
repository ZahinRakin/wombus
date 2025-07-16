from load_world import WorldLoader
from agent import Agent

def print_current_state(agent):
    print("Current World State:")
    for i in range(10):
        for j in range(10):
            print(agent.world.get_cell(i, j), end=' ')
        print()


def add_Breeze_and_Stench_To_Board(world):
    # Create a temporary agent to use the get_valid_neighbors method
    temp_agent = Agent(world, position=(0, 0))
    
    for i in range(10):
        for j in range(10):
            neighbors = temp_agent.get_valid_neighbors(i, j)
            if world.get_cell(i, j) == 'P':
                for n in neighbors:
                    if world.get_cell(n[0], n[1]) == '-':  # Only add breeze if cell is empty
                        world.set_cell(n[0], n[1], 'B')
                    elif world.get_cell(n[0], n[1]) == 'S':
                        world.set_cell(n[0], n[1], 'BS')
            elif world.get_cell(i, j) == 'W':
                for n in neighbors:
                    if world.get_cell(n[0], n[1]) == '-':
                        world.set_cell(n[0], n[1], 'S')
                    elif world.get_cell(n[0], n[1]) == 'B':
                        world.set_cell(n[0], n[1], 'BS')


def main():
    level = input("Enter the level (1-3): ")
    if level == '1':
        world = WorldLoader('easy.txt')
    elif level == '2':
        world = WorldLoader('medium.txt')
    elif level == '3':
        world = WorldLoader('world.txt')
    else:
        world = WorldLoader('none')  # Default to world.txt if invalid input
    add_Breeze_and_Stench_To_Board(world)  # This modifies the world in place
    expected_gold = count_gold = len(world.find_elements('G'))
    agent = Agent(world, position=(9, 0), expected_gold=expected_gold)

    agent.play_game()



if __name__ == "__main__":
    main()