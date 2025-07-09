#!/usr/bin/env python3
import sys
import argparse
from typing import Optional
from .game import WumpusGame
from ..agent.agent import Agent, AgentConfig
from ..environment.world_load import WorldLoader

def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Wumpus World Game")
    parser.add_argument('--world', default="worlds/default.world",
                       help="World file to load")
    parser.add_argument('--mode', choices=['auto', 'manual'], default='auto',
                       help="Game mode (auto/manual)")
    parser.add_argument('--no-gui', action='store_true',
                       help="Disable graphical interface")
    parser.add_argument('--difficulty', choices=['easy', 'medium', 'hard'],
                       help="Set difficulty level")
    return parser.parse_args()

def main() -> None:
    """Main game entry point"""
    args = parse_args()
    
    try:
        # Initialize game
        world_file = select_world_file(args)
        agent = create_agent(args.difficulty)
        
        game = WumpusGame(
            world_file=world_file,
            agent=agent,
            graphics=not args.no_gui
        )
        
        # Run in selected mode
        if args.mode == 'auto':
            game.run_autonomous()
        else:
            run_manual_mode(game)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def select_world_file(args: argparse.Namespace) -> str:
    """Select appropriate world file based on args"""
    if args.difficulty:
        return f"worlds/{args.difficulty}.world"
    return args.world

def create_agent(difficulty: Optional[str]) -> Agent:
    """Create agent with appropriate configuration"""
    config = AgentConfig()
    
    if difficulty == 'hard':
        config.arrow_count = 1
        config.death_penalty = 2000
    elif difficulty == 'medium':
        config.arrow_count = 2
        config.death_penalty = 1500
    else:  # easy/default
        config.arrow_count = 3
        config.death_penalty = 1000
        
    return Agent(config)

def run_manual_mode(game: WumpusGame) -> None:
    """Run game in manual control mode"""
    print("\nManual Control Mode")
    print("Use game.execute_action(action, direction) to play")
    print("Actions: 'move', 'shoot', 'grab'")
    print("Directions: 'up', 'down', 'left', 'right'")
    
    # Example manual control loop
    while not game.game_over:
        try:
            action = input("Enter action (or 'quit'): ").strip().lower()
            if action == 'quit':
                break
                
            if action in ['move', 'shoot']:
                direction = input(f"Enter direction for {action}: ").strip().lower()
                success, message = game.execute_action(action, direction)
            elif action == 'grab':
                success, message = game.execute_action(action)
            else:
                print("Invalid action")
                continue
                
            print(message)
            
        except KeyboardInterrupt:
            print("\nGame interrupted")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()