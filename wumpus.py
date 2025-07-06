#!/usr/bin/env python3
"""
Wumpus World Game - Main Entry Point

A simple console-based implementation of the classic Wumpus World AI problem.
"""

from game import WumpusGame
from agent import AgentConfig


class WumpusWorldConsole:
    """Console interface for the Wumpus World game"""
    
    def __init__(self, world_file='world.txt'):
        self.game = None
        self.world_file = world_file
        self.setup_game()
    
    def setup_game(self):
        """Initialize the game with default or custom configuration"""
        try:
            # Create agent configuration
            config = AgentConfig()
            # You can customize the configuration here
            # config.set_starting_position((9, 0))
            # config.set_costs_and_rewards(movement_cost=1, arrow_cost=10, gold_reward=1000)
            
            # Initialize game
            self.game = WumpusGame(self.world_file, config)
            print("🏛️  Welcome to Wumpus World! 🏛️")
            
        except Exception as e:
            print(f"Error setting up game: {e}")
            return False
        return True
    
    def print_instructions(self):
        """Print game instructions"""
        print("\n" + "="*60)
        print("OBJECTIVE:")
        print("  Find the gold and return to starting position (9,0)")
        print("\nCONTROLS:")
        print("  move <direction> - Move agent (up/down/left/right)")
        print("  grab             - Grab gold if present")
        print("  shoot <direction>- Shoot arrow in direction")
        print("  status           - Show current game status")
        print("  help             - Show this help")
        print("  reset            - Restart the game")
        print("  quit             - Quit game")
        print("\nLEGEND:")
        print("  A = Agent       W = Wumpus      P = Pit")
        print("  G = Gold        - = Empty       . = Visited")
        print("\nPERCEPTS:")
        print("  Stench   - Wumpus nearby")
        print("  Breeze   - Pit nearby")
        print("  Glitter  - Gold at current location")
        print("\nSCORING:")
        print("  Movement: -1    Arrow: -10    Gold: +1000")
        print("  Death: -1000    Win: Return safely with gold")
        print("="*60)
    
    def parse_command(self, command_str):
        """Parse user command into action and parameters"""
        parts = command_str.strip().lower().split()
        if not parts:
            return None, None
        
        action = parts[0]
        params = parts[1:] if len(parts) > 1 else []
        return action, params
    
    def execute_command(self, action, params):
        """Execute a game command"""
        if action == 'help':
            self.print_instructions()
            return True
        
        elif action == 'status':
            self.game.print_status()
            return True
        
        elif action == 'reset':
            self.game.reset_game()
            print("🔄 Game reset to initial state!")
            return True
        
        elif action == 'quit':
            print("👋 Thanks for playing Wumpus World!")
            return False
        
        elif action == 'move':
            if not params:
                print("❌ Please specify direction: move <up/down/left/right>")
                return True
            
            direction = params[0]
            if direction not in ['up', 'down', 'left', 'right']:
                print("❌ Invalid direction! Use: up, down, left, right")
                return True
            
            success, message = self.game.move_agent(direction)
            print(f"🚶 {message}")
            return True
        
        elif action == 'grab':
            success, message = self.game.grab_gold()
            print(f"🤏 {message}")
            return True
        
        elif action == 'shoot':
            if not params:
                print("❌ Please specify direction: shoot <up/down/left/right>")
                return True
            
            direction = params[0]
            if direction not in ['up', 'down', 'left', 'right']:
                print("❌ Invalid direction! Use: up, down, left, right")
                return True
            
            success, message = self.game.shoot_arrow(direction)
            print(f"🏹 {message}")
            return True
        
        else:
            print(f"❌ Unknown command: {action}")
            print("💡 Type 'help' for available commands")
            return True
    
    def play(self):
        """Main game loop"""
        if not self.game:
            print("❌ Game setup failed!")
            return
        
        self.print_instructions()
        print(f"\n🌍 World loaded successfully!")
        world_info = self.game.get_world_info()
        print(f"📍 World contains: {len(world_info['wumpus_positions'])} Wumpus, "
              f"{len(world_info['pit_positions'])} Pits, "
              f"{len(world_info['gold_positions'])} Gold")
        
        # Main game loop
        while True:
            # Display current state
            self.game.print_board()
            self.game.print_status()
            
            # Check if game is over
            if self.game.game_over:
                if self.game.won:
                    print(f"\n🎉 VICTORY! Final Score: {self.game.agent.score}")
                else:
                    print(f"\n💀 GAME OVER! Final Score: {self.game.agent.score}")
                
                # Ask if player wants to play again
                while True:
                    play_again = input("\n🔄 Play again? (y/n): ").strip().lower()
                    if play_again in ['y', 'yes']:
                        self.game.reset_game()
                        print("🔄 Game reset! Starting new game...")
                        break
                    elif play_again in ['n', 'no']:
                        print("👋 Thanks for playing!")
                        return
                    else:
                        print("❌ Please enter 'y' or 'n'")
                continue
            
            # Get user input
            try:
                command_str = input("\n💭 Enter command: ").strip()
                if not command_str:
                    continue
                
                action, params = self.parse_command(command_str)
                if action is None:
                    continue
                
                # Execute command
                continue_game = self.execute_command(action, params)
                if not continue_game:
                    break
                    
            except KeyboardInterrupt:
                print("\n\n🛑 Game interrupted!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break


def main():
    """Main function to start the game"""
    try:
        console = WumpusWorldConsole()
        console.play()
    except Exception as e:
        print(f"❌ Fatal error: {e}")


if __name__ == "__main__":
    main()
