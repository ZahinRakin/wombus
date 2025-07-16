import random
import time
from dataclasses import dataclass
from typing import Set, Tuple, List, Dict, Optional
from ..utils.constants import percepts

@dataclass
class AgentConfig:
    starting_position: Tuple[int, int] = (9, 0)
    movement_cost: int = 1
    arrow_count: int = 1
    arrow_cost: int = 10
    gold_reward: int = 1000
    death_penalty: int = 1000
    win_bonus: int = 500
    agent_symbol: str = 'A'
    trail_symbol: str = '.'
    expected_gold_count: int = 1

    def get_config(self) -> Dict:
        return {k: v for k, v in self.__dict__.items()}

class Agent:
    def __init__(self, agent_config: AgentConfig):
        self.agent_config = agent_config
        self.position = agent_config.starting_position
        self.starting_position = agent_config.starting_position
        self.path: List[Tuple[int, int]] = [self.position]
        self.arrow_count = agent_config.arrow_count
        self.gold_count = 0
        self.must_move = False
        self.is_alive = True
        self.score = 0
        self.action_history: List[str] = []
        self.position_history: List[Tuple[int, int]] = []

        # Knowledge base for tracking world state (from working version)
        self.knowledge_base = [[[] for _ in range(10)] for _ in range(10)]
        self.found_gold = 0
        self.expected_gold = agent_config.expected_gold_count
        self.step_count = 0
        self.game_won = False
        
        # Sensing information
        self.current_breeze = False
        self.current_stench = False
        self.current_cell_content = '-'
        
        # Event tracking for popups
        self.recent_events = []
        self.last_sensing_state = {"breeze": False, "stench": False}

        # Loop detection
        self.position_visit_count = {}
        self.last_actions = []
        
        # Risky move tracking
        self.consecutive_no_safe_moves = 0
        self.risky_move_threshold = 3  # Number of consecutive no-safe-moves before taking risky move

        self.directions = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }

    def get_position(self) -> Tuple[int, int]:
        return self.position

    def set_position(self, new_position: Tuple[int, int]) -> None:
        self.position = new_position

    def get_next_position(self, direction: str) -> Optional[Tuple[int, int]]:
        if direction not in self.directions:
            return None
        dr, dc = self.directions[direction]
        row, col = self.position
        if 0 <= row + dr < 10 and 0 <= col + dc < 10:
            return (row + dr, col + dc)
        return None

    def move(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        if pos:
            self.set_position(pos)
            self.score -= self.agent_config.movement_cost
            self.path.append(pos)
            
            # Track position visits for loop detection
            self.position_visit_count[pos] = self.position_visit_count.get(pos, 0) + 1
            
            return pos
        return None

    def grab_gold(self) -> bool:
        self.gold_count += 1
        self.found_gold += 1
        self.score += self.agent_config.gold_reward
        return True

    def shoot_arrow(self) -> bool:
        if self.arrow_count > 0:
            self.arrow_count -= 1
            self.score -= self.agent_config.arrow_cost
            return True
        return False

    def die(self) -> None:
        self.is_alive = False
        self.score -= self.agent_config.death_penalty

    def is_at_starting_position(self) -> bool:
        return self.position == self.starting_position

    def has_won(self) -> bool:
        return self.gold_count == self.agent_config.expected_gold_count

    def get_random_direction(self) -> str:
        d_int = random.randint(1, 4)
        if d_int == 1:
            return "left"
        if d_int == 2:
            return "right"
        if d_int == 3:
            return "up"
        if d_int == 4:
            return "down"
        return "right"

    def get_neighbors(self) -> List[Tuple[int, int]]:
        neighbors = []
        for dr, dc in self.directions.values():
            nr, nc = self.position[0] + dr, self.position[1] + dc
            if 0 <= nr < 10 and 0 <= nc < 10:
                neighbors.append((nr, nc))
        return neighbors

    def get_valid_neighbors(self, x, y):
        """Get valid neighboring cells that are not walls or hazards"""
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < 10 and 0 <= new_y < 10:
                neighbors.append((new_x, new_y))
        return neighbors

    def _get_direction_to(self, target: Tuple[int, int]) -> Optional[str]:
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        if dx == 0:
            return 'right' if dy > 0 else 'left'
        if dy == 0:
            return 'down' if dx > 0 else 'up'
        return None

    def AI_play(self, percept: str):
        """Enhanced AI logic from working version"""
        global percepts
        
        # get the current cell
        current_x, current_y = self.position
        
        # Increment step count and decrease score
        self.step_count += 1
        self.score -= 1  # -1 for each step
        
        # Reset sensing information
        self.current_breeze = False
        self.current_stench = False

        # Get the valid neighboring cells
        valid_neighbors = self.get_valid_neighbors(current_x, current_y)

        # Mark the current position as visited
        if 'V' not in self.knowledge_base[current_x][current_y]:
            self.knowledge_base[current_x][current_y].append('V')

        # Add knowledge that this cell doesn't have gold (since we would have found it)
        if 'G' not in percept:
            self.knowledge_base[current_x][current_y].append('~G')

        # Check if Breeze is Present
        if 'B' in percept:
            self.current_breeze = True
            self.knowledge_base[current_x][current_y].append('B')
            for neighbor in valid_neighbors:
                if 'P?' not in self.knowledge_base[neighbor[0]][neighbor[1]]:
                    self.knowledge_base[neighbor[0]][neighbor[1]].append('P?')
        else:
            self.knowledge_base[current_x][current_y].append('~B')
            for neighbor in valid_neighbors:
                if '~P' not in self.knowledge_base[neighbor[0]][neighbor[1]]:
                    self.knowledge_base[neighbor[0]][neighbor[1]].append('~P')

        # Check if Stench is Present
        if 'S' in percept:
            self.current_stench = True
            self.knowledge_base[current_x][current_y].append('S')
            for neighbor in valid_neighbors:
                if 'W?' not in self.knowledge_base[neighbor[0]][neighbor[1]]:
                    self.knowledge_base[neighbor[0]][neighbor[1]].append('W?')
        else:
            self.knowledge_base[current_x][current_y].append('~S')
            for neighbor in valid_neighbors:
                if '~W' not in self.knowledge_base[neighbor[0]][neighbor[1]]:
                    self.knowledge_base[neighbor[0]][neighbor[1]].append('~W')

        # Update percepts for visited cells
        for neighbor in valid_neighbors:
            if 'V' in percepts[neighbor[0]][neighbor[1]]:
                if '~P' not in self.knowledge_base[neighbor[0]][neighbor[1]]:
                    self.knowledge_base[neighbor[0]][neighbor[1]].append('~P')
                if '~W' not in self.knowledge_base[neighbor[0]][neighbor[1]]:
                    self.knowledge_base[neighbor[0]][neighbor[1]].append('~W')

        # Check for new sensing events
        if self.is_alive:
            new_sensing_events = self.check_for_new_events()
            self.recent_events.extend(new_sensing_events)

    def choose_next_move(self):
        """Enhanced pathfinding with risky move logic when no safe moves available"""
        current_x, current_y = self.position
        neighbors = self.get_valid_neighbors(current_x, current_y)

        # First priority: Find unvisited safe neighbors
        unvisited_safe = []
        for x, y in neighbors:
            if ('V' not in self.knowledge_base[x][y] and 
                '~P' in self.knowledge_base[x][y] and 
                '~W' in self.knowledge_base[x][y]):
                unvisited_safe.append((x, y))
        
        # If we have unvisited safe neighbors, choose the least visited one
        if unvisited_safe:
            # Reset consecutive no safe moves counter
            self.consecutive_no_safe_moves = 0
            # Sort by visit count (prefer less visited)
            unvisited_safe.sort(key=lambda pos: self.position_visit_count.get(pos, 0))
            return self._get_direction_to(unvisited_safe[0])
        
        # If all gold is found, return to start
        if self.found_gold >= self.expected_gold:
            if self.position != self.starting_position:
                path_to_start = self.find_path_to_start()
                if path_to_start:
                    next_step = path_to_start[0]
                    return self._get_direction_to(next_step)
        
        # Find safe neighbors (visited or not)
        safe_neighbors = []
        for x, y in neighbors:
            if ('~P' in self.knowledge_base[x][y] and 
                '~W' in self.knowledge_base[x][y]):
                safe_neighbors.append((x, y))
        
        # If we have safe neighbors, prefer less visited ones
        if safe_neighbors:
            # Reset consecutive no safe moves counter
            self.consecutive_no_safe_moves = 0
            safe_neighbors.sort(key=lambda pos: self.position_visit_count.get(pos, 0))
            return self._get_direction_to(safe_neighbors[0])
        
        # If no safe moves, try to find a path to an unvisited safe cell
        unvisited_safe_cells = []
        for x in range(10):
            for y in range(10):
                if ('V' not in self.knowledge_base[x][y] and 
                    '~P' in self.knowledge_base[x][y] and 
                    '~W' in self.knowledge_base[x][y]):
                    unvisited_safe_cells.append((x, y))
        
        if unvisited_safe_cells:
            # Try to find a path to the nearest unvisited safe cell
            path = self.find_path_to_target(unvisited_safe_cells[0])
            if path:
                return self._get_direction_to(path[0])
        
        # Increment consecutive no safe moves counter
        self.consecutive_no_safe_moves += 1
        
        # RISKY MOVE LOGIC: If we've been stuck without safe moves for too long, take a risky move
        if self.consecutive_no_safe_moves >= self.risky_move_threshold:
            risky_move = self.choose_risky_move()
            if risky_move:
                print(f"Taking risky move after {self.consecutive_no_safe_moves} consecutive no-safe-moves")
                return risky_move
        
        # Last resort: backtrack intelligently
        if len(self.path) > 1:
            # Find a previous position that's safe and not recently visited
            for i in range(len(self.path) - 2, max(0, len(self.path) - 10), -1):
                prev_pos = self.path[i]
                if (prev_pos != self.position and 
                    '~P' in self.knowledge_base[prev_pos[0]][prev_pos[1]] and 
                    '~W' in self.knowledge_base[prev_pos[0]][prev_pos[1]]):
                    return self._get_direction_to(prev_pos)
        
        return None

    def choose_risky_move(self) -> Optional[str]:
        """Choose a risky move when no safe moves are available"""
        current_x, current_y = self.position
        neighbors = self.get_valid_neighbors(current_x, current_y)
        
        # Categorize neighbors by risk level
        unknown_neighbors = []  # Neighbors with no knowledge (could be anything)
        pit_suspected = []      # Neighbors suspected to have pits
        wumpus_suspected = []   # Neighbors suspected to have wumpus
        
        for x, y in neighbors:
            # Skip if we know for certain it's dangerous
            if ('P' in self.knowledge_base[x][y] or 
                'W' in self.knowledge_base[x][y]):
                continue
                
            # Check if it's completely unknown
            if (not any(item in self.knowledge_base[x][y] for item in ['P?', 'W?', '~P', '~W']) and
                'V' not in self.knowledge_base[x][y]):
                unknown_neighbors.append((x, y))
            # Check if only pit is suspected
            elif ('P?' in self.knowledge_base[x][y] and 
                  'W?' not in self.knowledge_base[x][y] and
                  '~W' in self.knowledge_base[x][y]):
                pit_suspected.append((x, y))
            # Check if only wumpus is suspected  
            elif ('W?' in self.knowledge_base[x][y] and 
                  'P?' not in self.knowledge_base[x][y] and
                  '~P' in self.knowledge_base[x][y]):
                wumpus_suspected.append((x, y))
        
        # Prefer unknown neighbors (lowest risk)
        if unknown_neighbors:
            target = random.choice(unknown_neighbors)
            return self._get_direction_to(target)
        
        # If we have arrows and there are wumpus-suspected neighbors, try shooting first
        if self.arrow_count > 0 and wumpus_suspected:
            target = random.choice(wumpus_suspected)
            direction = self._get_direction_to(target)
            if direction:
                # This will be handled in decide_action as a shoot action
                return None
        
        # If we must move and only have risky options, prefer pit over wumpus
        # (pit might be survivable with luck, wumpus is certain death)
        if pit_suspected:
            target = random.choice(pit_suspected)
            print(f"WARNING: Taking risky move to suspected pit at {target}")
            return self._get_direction_to(target)
        
        if wumpus_suspected:
            target = random.choice(wumpus_suspected)
            print(f"WARNING: Taking risky move to suspected wumpus at {target}")
            return self._get_direction_to(target)
        
        # If no risky moves available, return None
        return None

    def find_path_to_start(self) -> Optional[List[Tuple[int, int]]]:
        """Find a path back to the starting position using BFS"""
        from collections import deque
        
        start = self.position
        target = self.starting_position
        
        if start == target:
            return [target]
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            (current, path) = queue.popleft()
            
            for neighbor in self.get_valid_neighbors(current[0], current[1]):
                if (neighbor not in visited and 
                    '~P' in self.knowledge_base[neighbor[0]][neighbor[1]] and
                    '~W' in self.knowledge_base[neighbor[0]][neighbor[1]]):
                    new_path = path + [neighbor]
                    if neighbor == target:
                        return new_path[1:]  # Return path excluding current position
                    queue.append((neighbor, new_path))
                    visited.add(neighbor)
        
        return None  # No path found

    def find_path_to_target(self, target: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Find a path to a target position using BFS"""
        from collections import deque
        
        start = self.position
        
        if start == target:
            return [target]
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            (current, path) = queue.popleft()
            
            for neighbor in self.get_valid_neighbors(current[0], current[1]):
                if (neighbor not in visited and 
                    '~P' in self.knowledge_base[neighbor[0]][neighbor[1]] and
                    '~W' in self.knowledge_base[neighbor[0]][neighbor[1]]):
                    new_path = path + [neighbor]
                    if neighbor == target:
                        return new_path[1:]  # Return path excluding current position
                    queue.append((neighbor, new_path))
                    visited.add(neighbor)
        
        return None  # No path found

    def has_safe_moves(self) -> bool:
        """Check if agent has any safe moves available"""
        neighbors = self.get_valid_neighbors(self.position[0], self.position[1])
        for x, y in neighbors:
            if ('~P' in self.knowledge_base[x][y] and 
                '~W' in self.knowledge_base[x][y]):
                return True
        return False

    def is_in_loop(self) -> bool:
        """Detect if agent is stuck in a loop"""
        # Check if current position has been visited too many times
        current_visits = self.position_visit_count.get(self.position, 0)
        if current_visits > 3:
            return True
        
        # Check if we've been oscillating between same positions
        if len(self.path) < 6:
            return False
        
        recent_positions = self.path[-6:]
        position_counts = {}
        for pos in recent_positions:
            position_counts[pos] = position_counts.get(pos, 0) + 1
        
        # If any position appears more than 2 times in last 6 moves, we're likely in a loop
        for count in position_counts.values():
            if count > 2:
                return True
        
        return False

    def infer_wumpus_shoot(self, neighbors) -> Tuple[str, str]:
        """Enhanced Wumpus shooting logic with knowledge base"""
        pot_cells = []
        definite_wumpus = []
        
        # Check for definite wumpus locations (only one possible location for stench)
        for neighbor in neighbors:
            r, c = neighbor
            if 'W?' in self.knowledge_base[r][c] and '~W' not in self.knowledge_base[r][c]:
                pot_cells.append(neighbor)
                
                # Check if this is the only possible wumpus location
                # by counting other possible wumpus locations
                other_wumpus_candidates = 0
                for other_neighbor in neighbors:
                    or_r, or_c = other_neighbor
                    if (other_neighbor != neighbor and 
                        'W?' in self.knowledge_base[or_r][or_c] and 
                        '~W' not in self.knowledge_base[or_r][or_c]):
                        other_wumpus_candidates += 1
                
                if other_wumpus_candidates == 0:
                    definite_wumpus.append(neighbor)
        
        # Shoot at definite wumpus locations first
        if definite_wumpus:
            target = definite_wumpus[0]
            direction = self._get_direction_to(target)
            if direction:
                return "shoot", direction
        
        # If we have a stench and only one possible wumpus location, shoot
        if self.current_stench and len(pot_cells) == 1:
            direction = self._get_direction_to(pot_cells[0])
            if direction:
                return "shoot", direction
        
        # If we're in a loop and have arrows, shoot at suspected wumpus
        if self.is_in_loop() and len(pot_cells) > 0:
            target = random.choice(pot_cells)
            direction = self._get_direction_to(target)
            if direction:
                return "shoot", direction
        
        # If no safe moves and we're considering risky moves, shoot at wumpus suspects
        if (self.consecutive_no_safe_moves >= self.risky_move_threshold and 
            len(pot_cells) > 0):
            target = random.choice(pot_cells)
            direction = self._get_direction_to(target)
            if direction:
                return "shoot", direction
        
        # If we're stuck and have arrows, try shooting at any suspected wumpus
        if len(pot_cells) > 0 and not self.has_safe_moves():
            target = random.choice(pot_cells)
            direction = self._get_direction_to(target)
            if direction:
                return "shoot", direction
                
        return "pass", "pass"

    def infer_pit(self, neighbors) -> None:
        """Pit inference logic with knowledge base"""
        pot_cell = set()
        for neighbor in neighbors:
            r, c = neighbor
            if 'P?' in self.knowledge_base[r][c] and '~P' not in self.knowledge_base[r][c]:
                pot_cell.add((r, c))
        
        if len(pot_cell) == 1:
            r, c = pot_cell.pop()
            self.knowledge_base[r][c].append('P')
            if 'P?' in self.knowledge_base[r][c]:
                self.knowledge_base[r][c].remove('P?')

    def decide_action(self, percept: str) -> Tuple[str, str]:
        """Enhanced decision making with AI logic, loop prevention, and risky moves"""
        global percepts
        time.sleep(0.1)  # Reduced delay to prevent excessive waiting

        # Run AI analysis
        self.AI_play(percept)

        if self.gold_count == self.agent_config.expected_gold_count:
            return 'win', "congratulations!"

        if 'G' in percept and '~G' not in percept:
            return 'grab', "Grabbing gold"

        neighbors = self.get_neighbors()

        # Check for loop detection and force action if stuck
        if self.is_in_loop():
            if self.arrow_count > 0:
                action, direction = self.infer_wumpus_shoot(neighbors)
                if action == "shoot":
                    return action, direction
            
            # If we're in a loop and no arrows, try to break out with exploration
            for r, c in neighbors:
                if ('~P' in self.knowledge_base[r][c] and 
                    '~W' in self.knowledge_base[r][c] and
                    self.position_visit_count.get((r, c), 0) < 2):
                    direction = self._get_direction_to((r, c))
                    if direction:
                        return 'move', direction

        # Add inference if breeze or stench is detected
        if 'S' in percept:
            for r, c in neighbors:
                if 'V' in percepts[r][c]:
                    if '~W' not in self.knowledge_base[r][c]:
                        self.knowledge_base[r][c].append('~W')
                else:
                    if 'W?' not in self.knowledge_base[r][c]:
                        self.knowledge_base[r][c].append('W?')

        if 'B' in percept:
            for r, c in neighbors:
                if 'V' in percepts[r][c]:
                    if '~P' not in self.knowledge_base[r][c]:
                        self.knowledge_base[r][c].append('~P')
                else:
                    if 'P?' not in self.knowledge_base[r][c]:
                        self.knowledge_base[r][c].append('P?')

        # Infer pit locations
        self.infer_pit(neighbors)
        
        # Try shooting if we have arrows and good targets
        if self.arrow_count > 0:
            action, direction = self.infer_wumpus_shoot(neighbors)
            if action == "shoot":
                return action, direction

        # Use enhanced pathfinding with risky move logic
        next_direction = self.choose_next_move()
        if next_direction:
            return 'move', next_direction

        # If choose_next_move returned None but we should try risky moves
        if self.consecutive_no_safe_moves >= self.risky_move_threshold:
            risky_direction = self.choose_risky_move()
            if risky_direction:
                return 'move', risky_direction

        # Explore unknown neighbors if no threat known
        for r, c in neighbors:
            if ('V' not in percepts[r][c] and 
                'W?' not in self.knowledge_base[r][c] and 
                'P?' not in self.knowledge_base[r][c]):
                direction = self._get_direction_to((r, c))
                if direction:
                    return 'move', direction

        # If we're really stuck, try shooting at any suspected wumpus
        if self.arrow_count > 0:
            for r, c in neighbors:
                if 'W?' in self.knowledge_base[r][c]:
                    direction = self._get_direction_to((r, c))
                    if direction:
                        return 'shoot', direction

        # Emergency fallback: move to least visited safe neighbor
        safe_neighbors = []
        for r, c in neighbors:
            if ('~P' in self.knowledge_base[r][c] and 
                '~W' in self.knowledge_base[r][c]):
                safe_neighbors.append((r, c))
        
        if safe_neighbors:
            safe_neighbors.sort(key=lambda pos: self.position_visit_count.get(pos, 0))
            direction = self._get_direction_to(safe_neighbors[0])
            if direction:
                return 'move', direction

        # Final fallback: random move
        return 'move', self.get_random_direction()

    def check_for_new_events(self):
        """Check for new major percepts and return list of events"""
        new_events = []
        
        # Check for new breeze detection
        if self.current_breeze and not self.last_sensing_state["breeze"]:
            new_events.append({
                "type": "BREEZE",
                "message": "⚠️ BREEZE DETECTED!\nThere's a pit nearby!",
                "color": "orange"
            })
        
        # Check for new stench detection
        if self.current_stench and not self.last_sensing_state["stench"]:
            new_events.append({
                "type": "STENCH", 
                "message": "🦨 STENCH DETECTED!\nThe Wumpus is nearby!",
                "color": "red"
            })
        
        # Update last sensing state
        self.last_sensing_state["breeze"] = self.current_breeze
        self.last_sensing_state["stench"] = self.current_stench
        
        return new_events
    
    def add_gold_found_event(self):
        """Add gold found event"""
        return {
            "type": "GOLD",
            "message": f"💰 GOLD FOUND!\nGold collected: {self.found_gold}/{self.expected_gold}\n+1000 points!",
            "color": "gold"
        }
    
    def get_and_clear_events(self):
        """Get recent events and clear the list"""
        events = self.recent_events.copy()
        self.recent_events.clear()
        return events

    def get_status(self) -> Dict:
        return {
            'position': self.position,
            'arrow_count': self.arrow_count,
            'gold_count': self.gold_count,
            'is_alive': self.is_alive,
            'score': self.score,
        }

    def reset(self) -> None:
        self.position = self.starting_position
        self.arrow_count = self.agent_config.arrow_count
        self.gold_count = 0
        self.found_gold = 0
        self.is_alive = True
        self.score = 0
        self.step_count = 0
        self.game_won = False
        self.path = [self.starting_position]
        self.action_history.clear()
        self.position_history.clear()
        self.knowledge_base = [[[] for _ in range(10)] for _ in range(10)]
        self.recent_events = []
        self.last_sensing_state = {"breeze": False, "stench": False}
        self.must_move = False
        self.position_visit_count = {}
        self.last_actions = []
        self.consecutive_no_safe_moves = 0