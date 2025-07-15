#!/usr/bin/env python3
"""
Test script to debug percept detection in Wumpus World
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from game.game import WumpusGame
from agent.agent import Agent, AgentConfig

def test_percepts():
    """Test percept detection at different positions"""
    print("🧪 Testing Percept Detection")
    print("=" * 50)
    
    try:
        # Create game
        game = WumpusGame(world_file="worlds/world.txt", graphics=False)
        
        # Test initial position
        print(f"\n📍 Testing at starting position: {game.agent.position}")
        percepts = game.get_percepts()
        print(f"Percepts detected: {percepts}")
        
        # Show world layout for reference
        print("\n🗺️  World Layout:")
        game.print_board()
        
        # Test movement and percept detection
        test_positions = [
            ('up', 'Moving up'),
            ('up', 'Moving up again'),
            ('left', 'Moving left'),
            ('right', 'Moving right')
        ]
        
        for direction, description in test_positions:
            print(f"\n🚶 {description} ({direction})")
            
            # Check if move is valid
            next_pos = game.agent.get_next_position(direction)
            if next_pos:
                success, message = game.move_agent(direction)
                print(f"Move result: {message}")
                
                if success and not game.game_over:
                    percepts = game.get_percepts()
                    print(f"New position: {game.agent.position}")
                    print(f"Percepts: {percepts}")
                    
                    # Update agent knowledge
                    game.agent.update_knowledge(percepts)
                    
                    # Show knowledge base status
                    kb = game.agent.knowledge_base
                    print(f"Safe locations: {sorted(list(kb.safe_locations))}")
                    print(f"Possible wumpus: {sorted(list(kb.possible_wumpus))}")
                    print(f"Possible pits: {sorted(list(kb.possible_pits))}")
                    print(f"Confirmed wumpus: {sorted(list(kb.confirmed_wumpus))}")
                    print(f"Confirmed pits: {sorted(list(kb.confirmed_pits))}")
                else:
                    print(f"Game ended: {message}")
                    break
            else:
                print("Invalid move - out of bounds")
    
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_percepts()
