#!/usr/bin/env python3
"""
Simple main entry point for Wumpus World Game
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from game.game import WumpusGame
from agent.agent import Agent, AgentConfig

def main():
    """Main game entry point"""
    print("🏛️  Welcome to Wumpus World! 🏛️")
    print("=" * 50)
    
    try:
        # Create agent configuration
        config = AgentConfig()
        agent = Agent(config)
        
        # Initialize game
        game = WumpusGame(world_file="worlds/world.txt", agent=agent, graphics=False)
        
        print(f"🌍 World loaded successfully!")
        world_info = game.get_world_info()
        print(f"📍 World contains: {len(world_info['wumpus_positions'])} Wumpus, "
              f"{len(world_info['pit_positions'])} Pits, "
              f"{len(world_info['gold_positions'])} Gold")
        
        # Show initial state
        game.print_board()
        game.print_status()
        
        print("\n📝 Commands:")
        print("  move <direction>  - Move agent (up/down/left/right)")
        print("  shoot <direction> - Shoot arrow (up/down/left/right)")
        print("  grab             - Grab gold at current position")
        print("  status           - Show current game status")
        print("  board            - Show board with percept indicators")
        print("  auto             - Let agent decide automatically")
        print("  test             - Test percept detection")
        print("  help             - Show this help")
        print("  quit             - Exit game")
        print("-" * 50)
        
        # Main game loop
        while not game.game_over:
            try:
                user_input = input("\n🎯 Enter command: ").strip().lower()
                
                if user_input == 'quit':
                    print("👋 Thanks for playing!")
                    break
                elif user_input == 'help':
                    print("\n📝 Available commands:")
                    print("  move up/down/left/right")
                    print("  shoot up/down/left/right") 
                    print("  grab")
                    print("  status")
                    print("  board")
                    print("  auto")
                    print("  test")
                    print("  quit")
                    continue
                elif user_input == 'status':
                    game.print_status()
                    continue
                elif user_input == 'board':
                    game.print_board()
                    continue
                elif user_input == 'test':
                    # Test percept detection
                    percepts = game.get_percepts()
                    print(f"🧪 Current percepts: {percepts}")
                    game.agent.update_knowledge(percepts)
                    continue
                elif user_input == 'auto':
                    # Let agent decide
                    percepts = game.get_percepts()
                    action, param = game.agent.decide_action(percepts)
                    print(f"🤖 Agent decided: {action} {param}")
                    
                    if action == 'move':
                        success, message = game.move_agent(param)
                        print(f"🚶 {message}")
                    elif action == 'shoot':
                        success, message = game.shoot_arrow(param)
                        print(f"🏹 {message}")
                    elif action == 'grab':
                        success, message = game.grab_gold()
                        print(f"📦 {message}")
                    elif action == 'wait':
                        print(f"⏸️ {param}")
                        continue
                    elif action == 'win':
                        print(f"🎉 {param}")
                        break
                elif user_input == 'grab':
                    success, message = game.grab_gold()
                    print(f"📦 {message}")
                elif user_input.startswith('move '):
                    direction = user_input.split(' ', 1)[1] if len(user_input.split()) > 1 else ''
                    if direction in ['up', 'down', 'left', 'right']:
                        success, message = game.move_agent(direction)
                        print(f"🚶 {message}")
                    else:
                        print("❌ Invalid direction. Use: up, down, left, right")
                        continue
                elif user_input.startswith('shoot '):
                    direction = user_input.split(' ', 1)[1] if len(user_input.split()) > 1 else ''
                    if direction in ['up', 'down', 'left', 'right']:
                        success, message = game.shoot_arrow(direction)
                        print(f"🏹 {message}")
                    else:
                        print("❌ Invalid direction. Use: up, down, left, right")
                        continue
                else:
                    print("❌ Invalid command. Type 'help' for available commands.")
                    continue
                    
                # Show updated state after valid actions
                if not game.game_over and user_input not in ['status', 'help', 'test']:
                    game.print_board()
                    game.print_status()
                elif game.game_over:
                    game.print_board()
                    if game.won:
                        print("\n🎉 CONGRATULATIONS! You won!")
                    else:
                        print("\n💀 Game Over!")
                    print(f"Final Score: {game.agent.get_status()['score']}")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Game interrupted. Thanks for playing!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error setting up game: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
