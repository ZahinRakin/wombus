#!/usr/bin/env python3
"""
Debug version of Wumpus World Game - shows agent's decision making process
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from gui_improved import WumpusWorldGUI
import time

class DebugWumpusWorldGUI(WumpusWorldGUI):
    def __init__(self):
        super().__init__()
        self.root.geometry("1400x800")  # Larger window for debug info
        # self.step_delay = 1.5  # Slower for debugging
        self.step_delay = 0.5  # Faster for debugging, adjust as needed
        self.add_debug_panel()
        
    def add_debug_panel(self):
        """Add debug information panel"""
        # Create debug frame
        debug_frame = ttk.LabelFrame(self.root, text="Debug Information", padding=10)
        debug_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False, padx=10, pady=5)
        
        # Create notebook for different debug tabs
        debug_notebook = ttk.Notebook(debug_frame)
        debug_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Agent Status Tab
        status_frame = ttk.Frame(debug_notebook)
        debug_notebook.add(status_frame, text="Agent Status")
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=8, width=60)
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Knowledge Base Tab
        kb_frame = ttk.Frame(debug_notebook)
        debug_notebook.add(kb_frame, text="Knowledge Base")
        
        self.kb_text = scrolledtext.ScrolledText(kb_frame, height=8, width=60)
        self.kb_text.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # Path & Moves Tab
        path_frame = ttk.Frame(debug_notebook)
        debug_notebook.add(path_frame, text="Path & Moves")
        
        self.path_text = scrolledtext.ScrolledText(path_frame, height=8, width=60)
        self.path_text.pack(fill=tk.BOTH, expand=True, padx=5)
        
    def update_debug_info(self, step_count):
        """Update all debug information"""
        if not self.agent:
            return
            
        # Update Agent Status
        self.status_text.delete(1.0, tk.END)
        status_info = f"""STEP {step_count}
Current Position: {self.agent.current_position}
Starting Position: {self.agent.starting_position}
Direction: {self.agent.direction}
Gold Found: {self.agent.found_gold}/{self.agent.expected_gold}
Path Length: {len(self.agent.path)}
Next Cells to Explore: {len(self.agent.next_cells)}

Valid Neighbors: {self.agent.get_valid_neighbors(*self.agent.current_position)}
"""
        self.status_text.insert(tk.END, status_info)
        
        # Update Knowledge Base (current position knowledge)
        self.kb_text.delete(1.0, tk.END)
        current_x, current_y = self.agent.current_position
        kb_info = f"Knowledge Base Summary:\n\n"
        
        # Show knowledge for explored cells
        explored_cells = []
        for i in range(10):
            for j in range(10):
                if 'V' in self.agent.knowledge_base[i][j]:
                    explored_cells.append((i, j))
        
        kb_info += f"Explored Cells ({len(explored_cells)}): {explored_cells[:10]}\n"
        if len(explored_cells) > 10:
            kb_info += f"... and {len(explored_cells) - 10} more\n"
            
        kb_info += f"\nCurrent Position Knowledge: {self.agent.knowledge_base[current_x][current_y]}\n\n"
        
        # Show safe cells
        safe_cells = []
        dangerous_cells = []
        for i in range(10):
            for j in range(10):
                kb = self.agent.knowledge_base[i][j]
                if '~P' in kb and '~W' in kb:
                    safe_cells.append((i, j))
                elif 'P?' in kb or 'W?' in kb:
                    dangerous_cells.append((i, j))
        
        kb_info += f"Known Safe Cells: {len(safe_cells)}\n"
        kb_info += f"Potentially Dangerous: {len(dangerous_cells)}\n"
        
        self.kb_text.insert(tk.END, kb_info)
        
        # Update Path & Moves
        self.path_text.delete(1.0, tk.END)
        path_info = f"Current Path: {self.agent.path}\n\n"
        path_info += f"Next Cells Queue: {self.agent.next_cells[:5]}\n"
        if len(self.agent.next_cells) > 5:
            path_info += f"... and {len(self.agent.next_cells) - 5} more\n\n"
        
        # Show recent moves (last 10)
        if hasattr(self, 'move_history'):
            path_info += "Recent Moves:\n"
            for move in self.move_history[-10:]:
                path_info += f"  {move}\n"
        
        self.path_text.insert(tk.END, path_info)
        
    def game_loop(self):
        """Debug game loop with detailed logging"""
        self.update_status("Game running (Debug Mode)...")
        self.move_history = []
        
        step_count = 0
        max_steps = 1000
        
        while self.game_running and step_count < max_steps:
            try:
                # Update debug info
                self.update_debug_info(step_count)
                
                # Check win condition
                if self.agent.found_gold >= self.agent.expected_gold:
                    self.update_status(f"Victory! All {self.agent.expected_gold} gold found!")
                    self.show_game_over(f"Victory! All {self.agent.expected_gold} gold collected!")
                    break
                
                # Show current status
                current_pos = self.agent.current_position
                print(f"Step {step_count + 1}: Agent at {current_pos}, Gold: {self.agent.found_gold}/{self.agent.expected_gold}")
                
                # AI makes a move
                self.agent.AI_play()
                
                # Choose next move
                next_move = self.agent.choose_next_move()
                print(f"  Next move chosen: {next_move}")
                
                if not next_move:
                    self.update_status("Game Over! No safe moves available.")
                    self.show_game_over("Game Over! No safe moves available.")
                    break
                
                # Validate move before executing
                if next_move == current_pos:
                    print(f"  ERROR: Invalid move - trying to move to same position {current_pos}")
                    self.update_status("Error: Agent stuck - trying to move to same position")
                    break
                
                # Move agent
                move_success = self.agent.move(*next_move)
                if not move_success:
                    print(f"  Move failed from {current_pos} to {next_move}")
                    break
                    
                print(f"  Agent moved successfully to: {next_move}")
                self.move_history.append(f"Step {step_count + 1}: {current_pos} → {next_move}")
                
                # Update display
                self.draw_world()
                self.gold_label.config(text=f"Gold Found: {self.agent.found_gold}/{self.agent.expected_gold}")
                
                # Check if returned to start (only after collecting all gold)
                if (next_move == self.agent.starting_position and 
                    self.agent.found_gold >= self.agent.expected_gold):
                    self.update_status("Victory! Returned to start with all gold!")
                    self.show_game_over("Game complete! Returned to starting position with all gold.")
                    break
                
                step_count += 1
                time.sleep(self.step_delay)  # Slower for debugging
                
            except Exception as e:
                print(f"Error in step {step_count}: {str(e)}")
                import traceback
                traceback.print_exc()
                self.update_status(f"Error: {str(e)}")
                break
        
        if step_count >= max_steps:
            self.update_status("Debug: Game stopped after maximum exploration steps.")
            self.show_game_over("Debug: The agent has explored for the maximum allowed steps.")
        
        print(f"Game ended after {step_count} steps")
        self.game_running = False
        self.start_btn.config(state="normal")

if __name__ == "__main__":
    print("Starting Debug Wumpus World GUI...")
    app = DebugWumpusWorldGUI()
    app.run()
