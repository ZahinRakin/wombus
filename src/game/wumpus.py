#!/usr/bin/env python3
import sys
import pygame
from .game import WumpusGame
from ..agent.agent import Agent, AgentConfig

def main() -> None:
    """Simplified game entry point for autonomous mode only"""
    try:
        agent = Agent(AgentConfig())
        game = WumpusGame(
            world_file="worlds/default.txt",
            agent=agent,
            graphics=True
        )

        while not game.game_over:
            game.run_autonomous()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
