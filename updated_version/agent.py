class Agent:
    def __init__(self, world, position=(9, 0), expected_gold=1):
        self.world = world
        self.knowledge_base = [[[] for _ in range(10)] for _ in range(10)]
        self.starting_position = position
        self.current_position = position
        self.direction = 'up'
        
        # Scoring system
        self.score = 0  # Start with 0 score
        self.step_count = 0
        self.is_alive = True
        self.game_won = False
        
        # Sensing information
        self.current_breeze = False
        self.current_stench = False
        
        # Check for gold at starting position before placing agent
        if self.world.get_cell(position[0], position[1]) == 'G':
            self.found_gold = 1
            self.score += 1000  # Gold bonus
            self.knowledge_base[position[0]][position[1]].append('G')
        else:
            self.found_gold = 0
            
        self.world.set_cell(position[0], position[1], 'A')
        self.path = []
        self.next_cells = []
        self.expected_gold = expected_gold


    def AI_play(self):
        
        # get the current cell
        current_x, current_y = self.current_position
        self.path.append((current_x, current_y))
        
        # Increment step count and decrease score
        self.step_count += 1
        self.score -= 1  # -1 for each step
        
        # Reset sensing information
        self.current_breeze = False
        self.current_stench = False

        #get the valid neighboring cells
        valid_neighbors = self.get_valid_neighbors(current_x, current_y)

        # Collect next cells to explore
        self.next_cells.extend(valid_neighbors)

        # Mark the current position as visited
        self.knowledge_base[current_x][current_y].append('V')

        # Add knowledge that this cell doesn't have gold (since we would have found it in move())
        self.knowledge_base[current_x][current_y].append('~G')

        # Check if Breeze is Present
        if self.world.get_cell(current_x, current_y) == 'B':
            self.current_breeze = True
            self.knowledge_base[current_x][current_y].append('B')
            for neighbor in valid_neighbors:
                self.knowledge_base[neighbor[0]][neighbor[1]].append('P?')
        else:
            self.knowledge_base[current_x][current_y].append('~B')
            for neighbor in valid_neighbors:
                self.knowledge_base[neighbor[0]][neighbor[1]].append('~P')

        # Check if Stench is Present
        if self.world.get_cell(current_x, current_y) == 'S':
            self.current_stench = True
            self.knowledge_base[current_x][current_y].append('S')
            for neighbor in valid_neighbors:
                self.knowledge_base[neighbor[0]][neighbor[1]].append('W?')
        else:
            self.knowledge_base[current_x][current_y].append('~S')
            for neighbor in valid_neighbors:
                self.knowledge_base[neighbor[0]][neighbor[1]].append('~W')

        # Check if Stench and Breeze are Present
        if self.world.get_cell(current_x, current_y) == 'BS':
            self.current_breeze = True
            self.current_stench = True
            self.knowledge_base[current_x][current_y].append('B')
            self.knowledge_base[current_x][current_y].append('S')
            for neighbor in valid_neighbors:
                self.knowledge_base[neighbor[0]][neighbor[1]].append('P?')
                self.knowledge_base[neighbor[0]][neighbor[1]].append('W?')

        # Check if Pit is Present (agent dies)
        if self.world.get_cell(current_x, current_y) == 'P':
            self.knowledge_base[current_x][current_y].append('P')
            self.is_alive = False
            self.score -= 1000  # Death penalty
        else:
            self.knowledge_base[current_x][current_y].append('~P')
        
        # Check if Wumpus is Present (agent dies)
        if self.world.get_cell(current_x, current_y) == 'W':
            self.knowledge_base[current_x][current_y].append('W')
            self.is_alive = False
            self.score -= 1000  # Death penalty
        else:
            self.knowledge_base[current_x][current_y].append('~W')
        if self.world.get_cell(current_x, current_y) == 'S':
            self.knowledge_base[current_x][current_y].append('S')
            for neighbor in valid_neighbors:
                self.knowledge_base[neighbor[0]][neighbor[1]].append('W?')
        else:
            self.knowledge_base[current_x][current_y].append('~S')
            for neighbor in valid_neighbors:
                self.knowledge_base[neighbor[0]][neighbor[1]].append('~W')

        # Check if Stench and Breeze are Present
        if self.world.get_cell(current_x, current_y) == 'BS':
            self.knowledge_base[current_x][current_y].append('B')
            self.knowledge_base[current_x][current_y].append('S')
            for neighbor in valid_neighbors:
                self.knowledge_base[neighbor[0]][neighbor[1]].append('P?')
                self.knowledge_base[neighbor[0]][neighbor[1]].append('W?')
        # else:
        #     self.knowledge_base[current_x][current_y].append('~BS')  # covered by previous checks

        # Check if Pit is Present
        if self.world.get_cell(current_x, current_y) == 'P':
            self.knowledge_base[current_x][current_y].append('P')
        else:
            self.knowledge_base[current_x][current_y].append('~P')
        
        # Check if Wumpus is Present
        if self.world.get_cell(current_x, current_y) == 'W':
            self.knowledge_base[current_x][current_y].append('W')
        else:
            self.knowledge_base[current_x][current_y].append('~W')

        # print("current self.knowledge_base:", self.knowledge_base)


    def choose_next_move(self):
        current_x, current_y = self.current_position
        neighbors = self.get_valid_neighbors(current_x, current_y)

        # First, try to find an unvisited safe neighbor
        for x, y in neighbors:
            if 'V' not in self.knowledge_base[x][y] and '~P' in self.knowledge_base[x][y] and '~W' in self.knowledge_base[x][y]:
                return (x, y)
        
        # If all gold is found, try to return to starting position
        if self.found_gold >= self.expected_gold:
            path_to_start = self.find_path_to_start()
            if path_to_start:
                next_step = path_to_start[0]
                # Ensure we don't return current position
                if next_step != self.current_position:
                    return next_step
            # Try direct movement to start if different from current position
            if self.starting_position != self.current_position:
                return self.starting_position
        
        # If no safe unvisited neighbors, backtrack
        if len(self.path) > 1:
            # Remove current position from path
            self.path.pop()
            # Get the previous position to backtrack to
            while self.path:
                prev_pos = self.path[-1]
                # Ensure we don't return current position
                if prev_pos != self.current_position:
                    return prev_pos
                else:
                    self.path.pop()  # Remove this position too and try the next one
        
        # Try to find any unexplored safe cell and navigate towards it
        exploration_target = self.get_next_exploration_target()
        if exploration_target:
            # For now, just try to move towards any safe neighbor that's not current position
            for x, y in neighbors:
                if ('~P' in self.knowledge_base[x][y] and 
                    '~W' in self.knowledge_base[x][y] and 
                    (x, y) != self.current_position):
                    return (x, y)
            
        # No valid moves available
        return None 

    def print_current_state(self):
        print("Current World State:")
        for i in range(10):
            for j in range(10):
                print(self.world.get_cell(i, j), end=' ')
            print()


    def play_game(self):
        while (1):
            if self.found_gold >= self.expected_gold:
                return "victory"

            
            self.AI_play()

            # Decide next move (you'll later make this smarter)
            next_move = self.choose_next_move()

            if not next_move:
                return "no_moves"

            self.move(*next_move)

            self.print_current_state()

            if next_move == self.starting_position:
                return "returned_home"



    def get_valid_neighbors(self, x, y):
        """Get valid neighboring cells that are not walls or hazards"""
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.world.world_size[0] and 0 <= new_y < self.world.world_size[1]:
                cell_content = self.world.get_cell(new_x, new_y)
                if cell_content not in ['W', 'P']:
                    neighbors.append((new_x, new_y))
        return neighbors



    def move(self, new_x, new_y):
        prev_pos = self.current_position
        
        # Validate the move - prevent moving to same position
        if (new_x, new_y) == prev_pos:
            print(f"Warning: Attempted invalid move to same position {prev_pos}")
            return False
        
        # Validate move is to adjacent cell
        dx = abs(new_x - prev_pos[0])
        dy = abs(new_y - prev_pos[1])
        if dx + dy != 1:  # Must be exactly one step away
            print(f"Warning: Attempted invalid move from {prev_pos} to ({new_x}, {new_y}) - not adjacent")
            return False
        
        # Check for gold at the new position BEFORE placing the agent
        if self.world.get_cell(new_x, new_y) == 'G':
            self.found_gold += 1
            self.score += 1000  # Gold bonus
            self.knowledge_base[new_x][new_y].append('G')
        
        # Update the world state
        self.world.set_cell(prev_pos[0], prev_pos[1], '+')
        self.current_position = (new_x, new_y)
        self.world.set_cell(new_x, new_y, 'A')

        # Update direction
        if new_x+1 == prev_pos[0]:
            self.direction = 'up'
        elif new_x-1 == prev_pos[0]:
            self.direction = 'down'
        elif new_y+1 == prev_pos[1]:
            self.direction = 'left'
        elif new_y-1 == prev_pos[1]:
            self.direction = 'right'
        
        return True

    def find_path_to_start(self):
        """Find a path back to the starting position using BFS"""
        from collections import deque
        
        start = self.current_position
        target = self.starting_position
        
        if start == target:
            return [target]
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            (current, path) = queue.popleft()
            
            for neighbor in self.get_valid_neighbors(current[0], current[1]):
                if neighbor not in visited and ('~P' in self.knowledge_base[neighbor[0]][neighbor[1]] 
                                              and '~W' in self.knowledge_base[neighbor[0]][neighbor[1]]):
                    new_path = path + [neighbor]
                    if neighbor == target:
                        return new_path[1:]  # Return path excluding current position
                    queue.append((neighbor, new_path))
                    visited.add(neighbor)
        
        return None  # No path found

    def get_next_exploration_target(self):
        """Find the next unexplored safe cell to visit"""
        for i in range(10):
            for j in range(10):
                if ('V' not in self.knowledge_base[i][j] and 
                    '~P' in self.knowledge_base[i][j] and 
                    '~W' in self.knowledge_base[i][j]):
                    return (i, j)
        return None
    
    def check_win_condition(self):
        """Check if the agent has won and apply win bonus"""
        if self.found_gold >= self.expected_gold and not self.game_won:
            self.game_won = True
            self.score += 500  # Win bonus
            return True
        return False
    
    def get_sensing_info(self):
        """Get current sensing information as a string"""
        sensing = []
        if self.current_breeze:
            sensing.append("BREEZE")
        if self.current_stench:
            sensing.append("STENCH")
        
        if sensing:
            return f"Sensing: {', '.join(sensing)}"
        else:
            return "Sensing: Nothing"


