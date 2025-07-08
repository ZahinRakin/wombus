import sys
import time
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from ..game.game import WumpusGame
from ..agent.agent import Agent, AgentConfig

class WumpusCLI:
    def __init__(self, world_file: str = "worlds/default.world"):
        self.game = WumpusGame(world_file, Agent(AgentConfig()), graphics=False)
        self.running = False
        self.commands = {
            'help': self._show_help,
            'move': self._move_agent,
            'shoot': self._shoot_arrow,
            'grab': self._grab_gold,
            'status': self._show_status,
            'quit': self._quit_game,
            'restart': self._restart_game
        }

    def run(self) -> None:
        """Main CLI game loop"""
        self.running = True
        self._show_welcome()
        
        while self.running:
            try:
                self._display_game_state()
                command = input("\nEnter command (type 'help' for options): ").strip().lower()
                self._process_command(command)
            except (KeyboardInterrupt, EOFError):
                print("\nGame interrupted!")
                self._quit_game()
            except Exception as e:
                print(f"Error: {e}")

    def _display_game_state(self) -> None:
        """Show current game state"""
        print("\n" + "=" * 40)
        print("Current Wumpus World State:")
        
        # Print board
        board = self.game.get_world_info()
        print("\n  " + " ".join(str(i) for i in range(board['world_size'][1])))
        for i, row in enumerate(self.game.game_world):
            print(f"{i} " + " ".join(row))
        
        # Print agent status
        status = self.game.get_game_status()
        print(f"\nPosition: {status['position']}")
        print(f"Arrows: {status['arrow_count']}")
        print(f"Gold: {'Yes' if status['has_gold'] else 'No'}")
        print(f"Score: {status['score']}")
        print(f"Percepts: {status['percepts']}")

    def _process_command(self, command: str) -> None:
        """Handle player input"""
        parts = command.split()
        if not parts:
            return
            
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in self.commands:
            self.commands[cmd](args)
        else:
            print(f"Unknown command: {cmd}")

    def _show_welcome(self) -> None:
        """Display welcome message and instructions"""
        print("\n" + "=" * 40)
        print("Welcome to Wumpus World!")
        print("=" * 40)
        self._show_help()

    def _show_help(self, args: List[str] = None) -> None:
        """Display help information"""
        print("\nAvailable Commands:")
        print("  move <direction> - Move agent (up, down, left, right)")
        print("  shoot <direction> - Shoot arrow")
        print("  grab - Pick up gold")
        print("  status - Show current game state")
        print("  restart - Start new game")
        print("  quit - Exit game")
        print("  help - Show this help")
        print("\nLegends:")
        print("  A - Agent, W - Wumpus, P - Pit")
        print("  G - Gold, . - Visited, - - Empty")

    def _move_agent(self, args: List[str]) -> None:
        """Handle movement command"""
        if len(args) != 1 or args[0] not in ['up', 'down', 'left', 'right']:
            print("Usage: move <up|down|left|right>")
            return
            
        success, message = self.game._move_agent(args[0])
        print(f"\n{message}")
        self._check_game_over()

    def _shoot_arrow(self, args: List[str]) -> None:
        """Handle shooting command"""
        if len(args) != 1 or args[0] not in ['up', 'down', 'left', 'right']:
            print("Usage: shoot <up|down|left|right>")
            return
            
        success, message = self.game._shoot_arrow(args[0])
        print(f"\n{message}")

    def _grab_gold(self, args: List[str] = None) -> None:
        """Handle gold grabbing"""
        success, message = self.game._grab_gold()
        print(f"\n{message}")
        self._check_game_over()

    def _show_status(self, args: List[str] = None) -> None:
        """Show detailed game status"""
        status = self.game.get_game_status()
        print("\nDetailed Status:")
        for key, value in status.items():
            print(f"{key.capitalize()}: {value}")

    def _restart_game(self, args: List[str] = None) -> None:
        """Restart the game"""
        self.game.reset_game()
        print("\nGame restarted!")

    def _quit_game(self, args: List[str] = None) -> None:
        """Exit the game"""
        self.running = False
        print("\nThanks for playing Wumpus World!")
        time.sleep(1)
        sys.exit(0)

    def _check_game_over(self) -> None:
        """Handle game over conditions"""
        status = self.game.get_game_status()
        if status['game_over']:
            if status['won']:
                print("\nCongratulations! You won the game!")
            else:
                print("\nGame Over! You failed.")
            
            play_again = input("Play again? (y/n): ").lower()
            if play_again == 'y':
                self._restart_game()
            else:
                self._quit_game()

def main():
    """Entry point for CLI version"""
    try:
        world_file = sys.argv[1] if len(sys.argv) > 1 else "worlds/default.world"
        cli = WumpusCLI(world_file)
        cli.run()
    except Exception as e:
        print(f"Error starting game: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()