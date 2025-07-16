import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from load_world import WorldLoader
from agent import Agent

class WumpusWorldGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Wumpus World Game")
        self.root.geometry("1200x700")
        
        # Game state
        self.world = None
        self.original_world = None  # Store original world state
        self.agent = None
        self.game_running = False
        self.canvas_size = 400
        self.cell_size = self.canvas_size // 10
        
        # Colors and symbols with color coding
        self.colors = {
            '-': 'white',
            'A': 'lightgreen',
            'W': 'red', 
            'P': 'black',
            'G': 'gold',
            'B': 'lightblue',
            'S': 'pink',
            'BS': 'purple',
            '+': 'lightgray'  # visited cell
        }
        
        # Text colors for symbols
        self.text_colors = {
            '-': 'black',
            'A': 'darkgreen',
            'W': 'darkred',
            'P': 'white',
            'G': 'darkgoldenrod',
            'B': 'darkblue',
            'S': 'darkmagenta',
            'BS': 'purple',
            '+': 'gray'
        }
        
        # Use clear text symbols
        self.symbols = {
            '-': '',
            'A': 'AGENT',
            'W': 'WUMPUS',
            'P': 'PIT',
            'G': 'GOLD',
            'B': 'BREEZE',
            'S': 'STENCH',
            'BS': 'B+S',
            '+': 'VISIT'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Wumpus World Game", font=("Arial", 20, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Menu frame
        menu_frame = ttk.LabelFrame(main_frame, text="Select World", padding=10)
        menu_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Difficulty buttons
        button_frame = ttk.Frame(menu_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Easy", command=lambda: self.start_game('easy.txt')).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Medium", command=lambda: self.start_game('medium.txt')).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Hard", command=lambda: self.start_game('hard.txt')).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Random", command=lambda: self.start_game('none')).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Choose File", command=self.choose_file).pack(side=tk.LEFT, padx=5)
        
        # Game frame
        game_frame = ttk.Frame(main_frame)
        game_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Current game
        left_frame = ttk.LabelFrame(game_frame, text="Current Game (Agent's Knowledge)", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.canvas = tk.Canvas(left_frame, width=self.canvas_size, height=self.canvas_size, bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.canvas.pack()
        
        # Middle - Original world reference
        middle_frame = ttk.LabelFrame(game_frame, text="Complete World (God's View)", padding=5)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.ref_canvas = tk.Canvas(middle_frame, width=self.canvas_size, height=self.canvas_size, bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.ref_canvas.pack()
        
        # Right side - Info panel
        info_frame = ttk.LabelFrame(game_frame, text="Game Info", padding=10)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status
        self.status_label = ttk.Label(info_frame, text="Select a world to start", font=("Arial", 11, "bold"), wraplength=150)
        self.status_label.pack(pady=(0, 10))
        
        # Gold counter
        self.gold_label = ttk.Label(info_frame, text="Gold Found: 0/0", font=("Arial", 10))
        self.gold_label.pack(pady=(0, 10))
        
        # Legend
        legend_frame = ttk.LabelFrame(info_frame, text="Legend", padding=5)
        legend_frame.pack(fill=tk.X, pady=(0, 10))
        
        legend_items = [
            ("AGENT = AI Player", "lightgreen", "darkgreen"),
            ("GOLD = Treasure", "gold", "darkgoldenrod"),
            ("WUMPUS = Monster", "red", "darkred"),
            ("PIT = Death Trap", "black", "white"),
            ("BREEZE = Near Pit", "lightblue", "darkblue"),
            ("STENCH = Near Wumpus", "pink", "darkmagenta"),
            ("VISIT = Explored", "lightgray", "gray")
        ]
        
        for text, bg_color, text_color in legend_items:
            frame = ttk.Frame(legend_frame)
            frame.pack(fill=tk.X, pady=1)
            color_box = tk.Label(frame, text="  ", bg=bg_color, relief=tk.RAISED, width=2)
            color_box.pack(side=tk.LEFT)
            label = ttk.Label(frame, text=text, font=("Arial", 8))
            label.pack(side=tk.LEFT, padx=(3, 0))
        
        # Control buttons
        control_frame = ttk.Frame(info_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_btn = ttk.Button(control_frame, text="Start Game", command=self.run_game, state=tk.DISABLED)
        self.start_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.reset_btn = ttk.Button(control_frame, text="Reset", command=self.reset_game, state=tk.DISABLED)
        self.reset_btn.pack(fill=tk.X)
        
    def choose_file(self):
        file_path = filedialog.askopenfilename(
            title="Select World File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.start_game(file_path)
    
    def start_game(self, world_file):
        try:
            # Load world
            self.world = WorldLoader(world_file)
            
            # Store original world state (deep copy)
            self.original_world = WorldLoader(world_file)
            
            self.add_breeze_and_stench()
            
            # Count gold
            expected_gold = len(self.world.find_elements('G'))
            
            # Create agent
            self.agent = Agent(self.world, position=(9, 0), expected_gold=expected_gold)
            
            # Update UI
            self.draw_world()
            self.draw_reference_world()
            self.update_status("Game loaded. Click 'Start Game' to begin.")
            self.gold_label.config(text=f"Gold Found: {self.agent.found_gold}/{expected_gold}")
            
            # Enable buttons
            self.start_btn.config(state=tk.NORMAL)
            self.reset_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load world: {str(e)}")
    
    def add_breeze_and_stench(self):
        """Add breeze and stench to the world based on pits and wumpus"""
        # Create a temporary agent to use the get_valid_neighbors method
        temp_agent = Agent(self.world, position=(0, 0))
        
        for i in range(10):
            for j in range(10):
                neighbors = temp_agent.get_valid_neighbors(i, j)
                if self.world.get_cell(i, j) == 'P':
                    for n in neighbors:
                        if self.world.get_cell(n[0], n[1]) == '-':
                            self.world.set_cell(n[0], n[1], 'B')
                        elif self.world.get_cell(n[0], n[1]) == 'S':
                            self.world.set_cell(n[0], n[1], 'BS')
                elif self.world.get_cell(i, j) == 'W':
                    for n in neighbors:
                        if self.world.get_cell(n[0], n[1]) == '-':
                            self.world.set_cell(n[0], n[1], 'S')
                        elif self.world.get_cell(n[0], n[1]) == 'B':
                            self.world.set_cell(n[0], n[1], 'BS')
    
    def draw_world(self):
        """Draw the current game world on the canvas"""
        self.canvas.delete("all")
        
        for i in range(10):
            for j in range(10):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                cell_content = self.world.get_cell(i, j)
                
                # Determine if cell is explored
                is_explored = (hasattr(self.agent, 'knowledge_base') and 
                             'V' in self.agent.knowledge_base[i][j])
                
                # Set background color
                if is_explored:
                    bg_color = self.colors.get(cell_content, 'lightgray')
                    if cell_content in ['-', 'A']:
                        bg_color = 'lightgray'  # Explored empty cells
                else:
                    bg_color = 'white'  # Unexplored cells
                
                # Draw cell
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg_color, outline='black', width=1)
                
                # Add symbol if explored or if it's the agent
                if is_explored or cell_content == 'A':
                    symbol = self.symbols.get(cell_content, '')
                    text_color = self.text_colors.get(cell_content, 'black')
                    if symbol:
                        # Use smaller font for the longer text
                        font_size = 8 if len(symbol) > 3 else 10
                        self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                              text=symbol, font=("Arial", font_size, "bold"), 
                                              fill=text_color)
                
                # Add grid coordinates (small text)
                self.canvas.create_text(x1 + 8, y1 + 8, text=f"{i},{j}", font=("Arial", 6), fill='gray')
        
        self.root.update()
    
    def draw_reference_world(self):
        """Draw the original world state for reference"""
        self.ref_canvas.delete("all")
        
        for i in range(10):
            for j in range(10):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                cell_content = self.original_world.get_cell(i, j)
                
                # Set background color
                bg_color = self.colors.get(cell_content, 'white')
                
                # Draw cell
                self.ref_canvas.create_rectangle(x1, y1, x2, y2, fill=bg_color, outline='black', width=1)
                
                # Add symbol
                symbol = self.symbols.get(cell_content, '')
                text_color = self.text_colors.get(cell_content, 'black')
                if symbol:
                    # Use smaller font for the longer text
                    font_size = 8 if len(symbol) > 3 else 10
                    self.ref_canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                              text=symbol, font=("Arial", font_size, "bold"), 
                                              fill=text_color)
                
                # Add grid coordinates (small text)
                self.ref_canvas.create_text(x1 + 8, y1 + 8, text=f"{i},{j}", font=("Arial", 6), fill='gray')
        
        self.root.update()
    
    def update_status(self, message):
        """Update the status label"""
        self.status_label.config(text=message)
        self.root.update()
    
    def run_game(self):
        """Run the game in a separate thread"""
        if not self.game_running:
            self.game_running = True
            self.start_btn.config(state=tk.DISABLED)
            threading.Thread(target=self.game_loop, daemon=True).start()
    
    def game_loop(self):
        """Main game loop"""
        self.update_status("Game running...")
        
        step_count = 0
        max_steps = 1000  # Increased limit to prevent premature stopping
        
        while self.game_running and step_count < max_steps:
            try:
                # Check win condition
                if self.agent.found_gold >= self.agent.expected_gold:
                    self.update_status("Victory! All gold found!")
                    self.show_game_over("Victory! All gold collected!")
                    break
                
                # AI makes a move
                self.agent.AI_play()
                
                # Choose next move
                next_move = self.agent.choose_next_move()
                
                if not next_move:
                    self.update_status("Game Over! No safe moves.")
                    self.show_game_over("Game Over! No safe moves available.")
                    break
                
                # Move agent
                if next_move == self.agent.current_position:
                    self.update_status("Error: Agent stuck - trying to move to same position")
                    self.show_game_over("Game Error: Agent is stuck and trying to move to the same position.")
                    break
                    
                move_success = self.agent.move(*next_move)
                if not move_success:
                    self.update_status("Error: Invalid move attempted")
                    self.show_game_over("Game Error: Agent attempted an invalid move.")
                    break
                
                # Update display
                self.draw_world()
                self.gold_label.config(text=f"Gold Found: {self.agent.found_gold}/{self.agent.expected_gold}")
                
                # Check if returned to start (only after collecting all gold)
                if (next_move == self.agent.starting_position and 
                    self.agent.found_gold >= self.agent.expected_gold):
                    self.update_status("Returned to start. Game complete!")
                    self.show_game_over("Game complete! Returned to starting position with all gold.")
                    break
                
                step_count += 1
                time.sleep(0.8)  # Delay for visualization
                
            except Exception as e:
                self.update_status(f"Error: {str(e)}")
                break
        
        if step_count >= max_steps:
            self.update_status("Game stopped: Agent may be stuck in exploration.")
            self.show_game_over("Game stopped: The agent has been exploring for a very long time. This might indicate the world is unsolvable or the agent is stuck.")
        
        self.game_running = False
        self.start_btn.config(state=tk.NORMAL)
    
    def show_game_over(self, message):
        """Show game over dialog"""
        def show_dialog():
            messagebox.showinfo("Game Over", message)
        
        self.root.after(0, show_dialog)
    
    def reset_game(self):
        """Reset the current game"""
        self.game_running = False
        if self.world and self.agent:
            # Reload the world
            world_file = self.world.file_path
            self.start_game(world_file)
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    gui = WumpusWorldGUI()
    gui.run()
