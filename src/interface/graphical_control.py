# import random
import pygame
import time
import math
from typing import List, Tuple, Dict
from pathlib import Path
from ..agent.agent import Agent

# Constants
TILE_SIZE = 60
ROWS, COLS = 10, 10
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE + 100  # Extra space for UI

# Modern color palette
COLORS = {
    'background': (20, 25, 40),
    'tile_empty': (45, 52, 70),
    'tile_border': (30, 35, 50),
    'player': (64, 224, 255),
    'player_glow': (30, 144, 255),
    'wumpus': (220, 20, 60),
    'wumpus_glow': (139, 0, 0),
    'gold': (255, 215, 0),
    'gold_glow': (255, 255, 0),
    'pit': (15, 15, 15),
    'pit_glow': (50, 50, 50),
    'victory': (50, 255, 50),
    'dead': (255, 50, 50),
    'ui_text': (200, 200, 200),
    'ui_bg': (35, 40, 55),
    'arrow': (255, 140, 0),
    'breeze': (100, 200, 255),      # Light blue for wind/air
    'stench': (255, 100, 100),      # Light red for danger/smell
    'trail': (100, 100, 100),
    'trail_glow': (150, 150, 150),
    'safe': (0, 100, 0, 50),        # Semi-transparent green
    'danger': (100, 0, 0, 50)       # Semi-transparent red
}

class WumpusGraphics:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Wumpus World AI Agent")
        self.clock = pygame.time.Clock()
        self.animation_time = time.time()
        
        # Load fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Load images if available
        self.images = self._load_images()
        
    def draw_glowing_circle(self, surface, center, radius, color, glow_color):
        """Draw a circle with a glowing effect"""
        # Draw multiple circles with decreasing alpha for glow effect
        for i in range(5):
            alpha = 50 - i * 10
            if alpha > 0:
                glow_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*glow_color, alpha), (radius * 2, radius * 2), radius + i * 3)
                surface.blit(glow_surf, (center[0] - radius * 2, center[1] - radius * 2))
        
        # Draw main circle
        pygame.draw.circle(surface, color, center, radius)

    def draw_pulsing_effect(self, surface, center, base_radius, color, time_offset=0):
        """Draw a pulsing effect"""
        pulse = math.sin(self.animation_time * 3 + time_offset) * 0.3 + 0.7
        radius = int(base_radius * pulse)
        alpha = int(255 * pulse * 0.5)
        
        if alpha > 0:
            pulse_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(pulse_surf, (*color, alpha), (radius * 2, radius * 2), radius)
            surface.blit(pulse_surf, (center[0] - radius * 2, center[1] - radius * 2))

    def draw_particle_trail(self, surface, center, color):
        """Draw trailing particles"""
        for i in range(8):
            offset_x = math.sin(self.animation_time * 2 + i * 0.8) * 15
            offset_y = math.cos(self.animation_time * 2 + i * 0.8) * 15
            alpha = int(255 * (1 - i / 8) * 0.3)
            
            if alpha > 0:
                particle_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, (*color, alpha), (3, 3), 3)
                surface.blit(particle_surf, (center[0] + offset_x - 3, center[1] + offset_y - 3))

    def draw_pit(self, surface, center):
        """Draw a pit with dark swirling effect"""
        # Draw dark center
        pygame.draw.circle(surface, COLORS['pit'], center, 15)
        
        # Draw swirling effect
        for i in range(3):
            angle = self.animation_time * 2 + i * 2.1
            radius = 8 + i * 3
            swirl_x = center[0] + math.cos(angle) * radius
            swirl_y = center[1] + math.sin(angle) * radius
            pygame.draw.circle(surface, COLORS['pit_glow'], (int(swirl_x), int(swirl_y)), 3)

    def draw_breeze(self, surface, center):
        """Draw breeze effect (indicates nearby pit) with wind symbol"""
        # Draw wind swirls
        for i in range(3):
            angle = self.animation_time * 2 + i * 2.1
            radius = 15 + i * 5
            start_angle = angle
            end_angle = angle + 1.5
            
            # Calculate arc points
            start_x = center[0] + math.cos(start_angle) * radius
            start_y = center[1] + math.sin(start_angle) * radius
            end_x = center[0] + math.cos(end_angle) * radius
            end_y = center[1] + math.sin(end_angle) * radius
            
            # Draw curved lines to represent wind
            pygame.draw.arc(surface, COLORS['breeze'], 
                          (center[0] - radius, center[1] - radius, radius * 2, radius * 2),
                          start_angle, end_angle, 3)
        
        # Add flowing particles
        for i in range(6):
            particle_angle = self.animation_time * 3 + i * 1.0
            particle_radius = 20 + math.sin(self.animation_time * 4 + i) * 5
            px = center[0] + math.cos(particle_angle) * particle_radius
            py = center[1] + math.sin(particle_angle) * particle_radius
            pygame.draw.circle(surface, COLORS['breeze'], (int(px), int(py)), 2)
        
        # Add "B" text indicator
        font = pygame.font.Font(None, 24)
        text = font.render("B", True, COLORS['breeze'])
        text_rect = text.get_rect(center=(center[0], center[1] + 25))
        surface.blit(text, text_rect)

    def draw_stench(self, surface, center):
        """Draw stench effect (indicates nearby Wumpus) with stink lines"""
        # Draw stench waves
        for i in range(4):
            wave_offset = math.sin(self.animation_time * 4 + i * 0.5) * 3
            y_pos = center[1] - 20 + i * 10 + wave_offset
            
            # Draw wavy stench lines
            points = []
            for x_offset in range(-20, 21, 4):
                wave_y = y_pos + math.sin((x_offset + self.animation_time * 50) * 0.3) * 2
                points.append((center[0] + x_offset, wave_y))
            
            if len(points) > 1:
                pygame.draw.lines(surface, COLORS['stench'], False, points, 2)
        
        # Add skull-like indicator for danger
        skull_center = (center[0], center[1] - 5)
        pygame.draw.circle(surface, COLORS['stench'], skull_center, 8)
        
        # Eyes
        pygame.draw.circle(surface, (0, 0, 0), (skull_center[0] - 3, skull_center[1] - 2), 2)
        pygame.draw.circle(surface, (0, 0, 0), (skull_center[0] + 3, skull_center[1] - 2), 2)
        
        # Add "S" text indicator
        font = pygame.font.Font(None, 24)
        text = font.render("S", True, COLORS['stench'])
        text_rect = text.get_rect(center=(center[0], center[1] + 25))
        surface.blit(text, text_rect)

    def animate_moving_arrow(self, start):
        pass

    def draw_wumpus(self, surface, center):
        self.draw_pulsing_effect(surface, center, 25, COLORS['wumpus_glow'])
        self.draw_glowing_circle(surface, center, 20, COLORS['wumpus'], COLORS['wumpus_glow'])
        
        # Add menacing eyes
        eye1_pos = (center[0] - 6, center[1] - 8)
        eye2_pos = (center[0] + 6, center[1] - 8)
        pygame.draw.circle(surface, (255, 0, 0), eye1_pos, 3)
        pygame.draw.circle(surface, (255, 0, 0), eye2_pos, 3)

    def draw_agent(self, surface, center):
        self.draw_particle_trail(surface, center, COLORS['player'])
        self.draw_glowing_circle(surface, center, 18, COLORS['player'], COLORS['player_glow'])
        
        # Add player "eye" or direction indicator
        eye_pos = (center[0] + 5, center[1] - 5)
        pygame.draw.circle(surface, (255, 255, 255), eye_pos, 3)

    def draw_gold(self, surface, center):
        self.draw_pulsing_effect(surface, center, 22, COLORS['gold_glow'])
        # Draw diamond shape for gold
        diamond_points = [
            (center[0], center[1] - 15),
            (center[0] + 12, center[1]),
            (center[0], center[1] + 15),
            (center[0] - 12, center[1])
        ]
        pygame.draw.polygon(surface, COLORS['gold'], diamond_points)
        pygame.draw.polygon(surface, COLORS['gold_glow'], diamond_points, 2)
        
        # Add sparkle effect
        for i in range(4):
            sparkle_x = center[0] + math.sin(self.animation_time * 4 + i * 1.5) * 20
            sparkle_y = center[1] + math.cos(self.animation_time * 4 + i * 1.5) * 20
            pygame.draw.circle(surface, (255, 255, 255), (int(sparkle_x), int(sparkle_y)), 2)

    def draw_trail(self, surface, center):
        # Draw a subtle dot to mark visited tiles
        pygame.draw.circle(surface, COLORS['trail'], center, 4)
        
        # Add a subtle glow effect around the dot
        pygame.draw.circle(surface, COLORS['trail_glow'], center, 8, 2)
        
        # Optional: Add a pulsing effect to make it more visible
        pulse_radius = 6 + int(2 * math.sin(self.animation_time * 3))
        pygame.draw.circle(surface, COLORS['trail'], center, pulse_radius, 1)

    def _draw_ui(self, agent: Agent, status: str) -> None:
        ui_y = ROWS * TILE_SIZE
        pygame.draw.rect(self.screen, COLORS['ui_bg'], (0, ui_y, WIDTH, 100))

        status_surf = self.font_large.render(f"Status: {status}", True, COLORS['ui_text'])
        self.screen.blit(status_surf, (10, ui_y + 10))

        info_lines = [
            f"Position: {agent.position}",
            f"Arrows: {agent.arrow_count}",
            f"Gold: {'Yes' if agent.has_gold else 'No'}",
            f"Score: {agent.score}"
        ]

        for i, line in enumerate(info_lines):
            text = self.font_medium.render(line, True, COLORS['ui_text'])
            self.screen.blit(text, (10, ui_y + 40 + i * 20))

    def animate_death(self):
        """Display a sad animation after death"""
        # Create a dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        
        # Animation loop
        for frame in range(60):
            self.screen.blit(overlay, (0, 0))
            
            # Pulsing red effect
            alpha = int(100 + 50 * math.sin(frame * 0.3))
            red_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            red_surf.fill((255, 0, 0, alpha))
            self.screen.blit(red_surf, (0, 0))
            
            # Death message
            death_text = self.font_large.render("YOU DIED", True, (255, 255, 255))
            text_rect = death_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            self.screen.blit(death_text, text_rect)
            
            # Sad face
            face_center = (WIDTH//2, HEIGHT//2 + 60)
            pygame.draw.circle(self.screen, (255, 255, 255), face_center, 30, 3)
            # Eyes
            pygame.draw.circle(self.screen, (255, 255, 255), (face_center[0] - 10, face_center[1] - 10), 3)
            pygame.draw.circle(self.screen, (255, 255, 255), (face_center[0] + 10, face_center[1] - 10), 3)
            # Sad mouth
            pygame.draw.arc(self.screen, (255, 255, 255), 
                        (face_center[0] - 15, face_center[1] + 5, 30, 20), 
                        0, math.pi, 3)
            
            pygame.display.flip()
            time.sleep(0.05)

    def animate_victory(self):
        """Display a happy animation after winning"""
        # Create a bright overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(100)
        overlay.fill((255, 255, 255))
        
        # Animation loop
        for frame in range(90):
            self.screen.blit(overlay, (0, 0))
            
            # Golden sparkles
            for i in range(20):
                sparkle_x = (frame * 3 + i * 30) % WIDTH
                sparkle_y = 50 + 30 * math.sin(frame * 0.1 + i)
                pygame.draw.circle(self.screen, (255, 215, 0), (int(sparkle_x), int(sparkle_y)), 3)
            
            # Victory message
            victory_text = self.font_large.render("VICTORY!", True, (50, 255, 50))
            text_rect = victory_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            self.screen.blit(victory_text, text_rect)
            
            # Happy face
            face_center = (WIDTH//2, HEIGHT//2 + 60)
            pygame.draw.circle(self.screen, (255, 255, 255), face_center, 30, 3)
            # Eyes
            pygame.draw.circle(self.screen, (255, 255, 255), (face_center[0] - 10, face_center[1] - 10), 3)
            pygame.draw.circle(self.screen, (255, 255, 255), (face_center[0] + 10, face_center[1] - 10), 3)
            # Happy mouth
            pygame.draw.arc(self.screen, (255, 255, 255), 
                        (face_center[0] - 15, face_center[1] + 5, 30, 15), 
                        math.pi, 2 * math.pi, 3)
            
            pygame.display.flip()
            time.sleep(0.03)

    def display_options(self):
        """Display options menu: restart, take snapshot, quit"""
        # Create menu overlay
        menu_overlay = pygame.Surface((WIDTH, HEIGHT))
        menu_overlay.set_alpha(200)
        menu_overlay.fill((0, 0, 0))
        self.screen.blit(menu_overlay, (0, 0))
        
        # Menu background
        menu_rect = pygame.Rect(WIDTH//4, HEIGHT//4, WIDTH//2, HEIGHT//2)
        pygame.draw.rect(self.screen, COLORS['ui_bg'], menu_rect)
        pygame.draw.rect(self.screen, COLORS['tile_border'], menu_rect, 3)
        
        # Menu title
        title_text = self.font_large.render("OPTIONS", True, COLORS['ui_text'])
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 80))
        self.screen.blit(title_text, title_rect)
        
        # Menu options
        options_text = [
            "R - Restart Game",
            "S - Take Snapshot",
            "Q - Quit Game",
            "ESC - Close Menu"
        ]
        
        for i, option in enumerate(options_text):
            option_surface = self.font_medium.render(option, True, COLORS['ui_text'])
            option_rect = option_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 30 + i * 35))
            self.screen.blit(option_surface, option_rect)
        
        pygame.display.flip()
        
        # Wait for user input
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return "restart"
                    elif event.key == pygame.K_s:
                        # Take screenshot
                        pygame.image.save(self.screen, f"wumpus_snapshot_{int(time.time())}.png")
                        return "snapshot"
                    elif event.key == pygame.K_q:
                        return "quit"
                    elif event.key == pygame.K_ESCAPE:
                        return "close"
                elif event.type == pygame.QUIT:
                    return "quit"
        
        return "close"

    def _load_images(self) -> Dict[str, pygame.Surface]:
        """Load graphical assets if available"""
        images = {}
        try:
            asset_path = Path("assets")
            if asset_path.exists():
                images['gold'] = pygame.image.load(asset_path / "gold.png").convert_alpha()
                images['wumpus'] = pygame.image.load(asset_path / "wumpus.png").convert_alpha()
        except:
            print("Could not load images, using default rendering")
        return images

    def draw_board(self, board: List[List[str]], agent: Agent, status: str = "Exploring") -> None:
        self.screen.fill(COLORS['background'])
        self.animation_time = time.time()

        for x in range(COLS + 1):
            pygame.draw.line(self.screen, COLORS['tile_border'], (x * TILE_SIZE, 0), (x * TILE_SIZE, ROWS * TILE_SIZE))
        for y in range(ROWS + 1):
            pygame.draw.line(self.screen, COLORS['tile_border'], (0, y * TILE_SIZE), (COLS * TILE_SIZE, y * TILE_SIZE))

        for y in range(ROWS):
            for x in range(COLS):
                self._draw_tile(x, y, board[y][x])

        self._draw_ui(agent, status)
        pygame.display.flip()
        self.clock.tick(60)

    def _draw_tile(self, x: int, y: int, tile_type: str) -> None:
        """Draw individual tile with animations"""
        pixel_x = x * TILE_SIZE
        pixel_y = y * TILE_SIZE
        center = (pixel_x + TILE_SIZE // 2, pixel_y + TILE_SIZE // 2)
        
        # Tile background
        tile_rect = pygame.Rect(pixel_x, pixel_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(self.screen, COLORS['tile_empty'], tile_rect)
        
        # Draw contents
        if tile_type == 'A':
            self.draw_agent(self.screen, center)
        elif tile_type == 'W':
            self.draw_wumpus(self.screen, center)
        elif tile_type == 'B':
            self.draw_breeze(self.screen, center)
        elif tile_type == 'S':
            self.draw_stench(self.screen, center)
        elif tile_type == 'G':
            self.draw_gold(self.screen, center)
        elif tile_type == 'P':
            self.draw_pit(self.screen, center)
        elif tile_type == '.':
            self.draw_trail(self.screen ,center)

    def close(self) -> None:
        """Clean up resources"""
        pygame.quit()

