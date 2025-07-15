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
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        pygame.display.toggle_fullscreen()
                    elif event.key == pygame.K_m:
                        pygame.display.iconify()

            game.run_autonomous()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
