import pygame
import time
import math

# Enhanced visual settings
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
    'victory': (50, 255, 50),
    'dead': (255, 50, 50),
    'ui_text': (200, 200, 200),
    'ui_bg': (35, 40, 55)
}

class wompus_graphics:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Wumpus World - Enhanced Edition")
        
        # Load fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Visual effects
        self.particle_effects = []
        
    def draw_glowing_circle(self, surface, center, radius, color, glow_color):
        """Draw a circle with a glowing effect"""
        # Draw multiple circles with decreasing alpha for glow effect
        for i in range(5):
            alpha = 50 - i * 10
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
        
        pulse_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(pulse_surf, (*color, alpha), (radius * 2, radius * 2), radius)
        surface.blit(pulse_surf, (center[0] - radius * 2, center[1] - radius * 2))

    def draw_particle_trail(self, surface, center, color):
        """Draw trailing particles"""
        for i in range(8):
            offset_x = math.sin(self.animation_time * 2 + i * 0.8) * 15
            offset_y = math.cos(self.animation_time * 2 + i * 0.8) * 15
            alpha = int(255 * (1 - i / 8) * 0.3)
            
            particle_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (*color, alpha), (3, 3), 3)
            surface.blit(particle_surf, (center[0] + offset_x - 3, center[1] + offset_y - 3))

    def draw_tile(self, x, y, tile_type):
        """Draw an individual tile with enhanced graphics"""
        pixel_x = x * TILE_SIZE
        pixel_y = y * TILE_SIZE
        center = (pixel_x + TILE_SIZE // 2, pixel_y + TILE_SIZE // 2)
        
        # Draw tile background with gradient effect
        tile_rect = pygame.Rect(pixel_x, pixel_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(self.screen, COLORS['tile_empty'], tile_rect)
        
        # Add subtle inner shadow
        pygame.draw.rect(self.screen, COLORS['tile_border'], tile_rect, 2)
        
        # Draw tile contents based on type
        if tile_type == 'P':  # Player
            self.draw_particle_trail(self.screen, center, COLORS['player'])
            self.draw_glowing_circle(self.screen, center, 18, COLORS['player'], COLORS['player_glow'])
            
            # Add player "eye" or direction indicator
            eye_pos = (center[0] + 5, center[1] - 5)
            pygame.draw.circle(self.screen, (255, 255, 255), eye_pos, 3)
            
        elif tile_type == 'W':  # Wumpus
            self.draw_pulsing_effect(self.screen, center, 25, COLORS['wumpus_glow'])
            self.draw_glowing_circle(self.screen, center, 20, COLORS['wumpus'], COLORS['wumpus_glow'])
            
            # Add menacing eyes
            eye1_pos = (center[0] - 6, center[1] - 8)
            eye2_pos = (center[0] + 6, center[1] - 8)
            pygame.draw.circle(self.screen, (255, 0, 0), eye1_pos, 3)
            pygame.draw.circle(self.screen, (255, 0, 0), eye2_pos, 3)
            
        elif tile_type == 'G':  # Gold
            self.draw_pulsing_effect(self.screen, center, 22, COLORS['gold_glow'])
            
            # Draw diamond shape for gold
            diamond_points = [
                (center[0], center[1] - 15),
                (center[0] + 12, center[1]),
                (center[0], center[1] + 15),
                (center[0] - 12, center[1])
            ]
            pygame.draw.polygon(self.screen, COLORS['gold'], diamond_points)
            pygame.draw.polygon(self.screen, COLORS['gold_glow'], diamond_points, 2)
            
            # Add sparkle effect
            for i in range(4):
                sparkle_x = center[0] + math.sin(self.animation_time * 4 + i * 1.5) * 20
                sparkle_y = center[1] + math.cos(self.animation_time * 4 + i * 1.5) * 20
                pygame.draw.circle(self.screen, (255, 255, 255), (int(sparkle_x), int(sparkle_y)), 2)
                
        elif tile_type == 'X':  # Dead
            self.draw_glowing_circle(self.screen, center, 20, COLORS['dead'], COLORS['dead'])
            
            # Draw X
            pygame.draw.line(self.screen, (255, 255, 255), 
                           (center[0] - 12, center[1] - 12), 
                           (center[0] + 12, center[1] + 12), 4)
            pygame.draw.line(self.screen, (255, 255, 255), 
                           (center[0] + 12, center[1] - 12), 
                           (center[0] - 12, center[1] + 12), 4)
                           
        elif tile_type == 'V':  # Victory
            self.draw_pulsing_effect(self.screen, center, 30, COLORS['victory'], math.pi)
            self.draw_glowing_circle(self.screen, center, 22, COLORS['victory'], COLORS['victory'])
            
            # Draw crown or star
            star_points = []
            for i in range(5):
                angle = i * 2 * math.pi / 5 - math.pi / 2
                outer_x = center[0] + math.cos(angle) * 15
                outer_y = center[1] + math.sin(angle) * 15
                star_points.append((outer_x, outer_y))
                
                angle += math.pi / 5
                inner_x = center[0] + math.cos(angle) * 8
                inner_y = center[1] + math.sin(angle) * 8
                star_points.append((inner_x, inner_y))
            
            pygame.draw.polygon(self.screen, (255, 255, 255), star_points)

    def draw_ui(self):
        """Draw the user interface"""
        ui_y = ROWS * TILE_SIZE
        ui_rect = pygame.Rect(0, ui_y, WIDTH, 100)
        pygame.draw.rect(self.screen, COLORS['ui_bg'], ui_rect)
        pygame.draw.line(self.screen, COLORS['tile_border'], (0, ui_y), (WIDTH, ui_y), 2)
        
        # Game status
        status_text = "WUMPUS WORLD"
        if self.victory_achieved:
            status_text = "VICTORY!"
        elif self.game_over:
            status_text = "GAME OVER"
        
        status_surface = self.font_large.render(status_text, True, COLORS['ui_text'])
        self.screen.blit(status_surface, (10, ui_y + 10))
        
        # Gold status
        gold_text = f"Gold: {'✓' if self.has_gold else '✗'}"
        gold_surface = self.font_medium.render(gold_text, True, COLORS['ui_text'])
        self.screen.blit(gold_surface, (10, ui_y + 45))
        
        # Position
        pos_text = f"Position: ({self.player_pos[0]}, {self.player_pos[1]})"
        pos_surface = self.font_medium.render(pos_text, True, COLORS['ui_text'])
        self.screen.blit(pos_surface, (10, ui_y + 70))
        
        # Controls hint
        controls_text = "Use arrow keys or WASD to move"
        controls_surface = self.font_small.render(controls_text, True, COLORS['ui_text'])
        self.screen.blit(controls_surface, (WIDTH - 220, ui_y + 75))

    def draw_board(self, board: list[list[str]]):
        """Draw the entire game board"""
        self.screen.fill(COLORS['background'])
        
        # Update animation time
        self.animation_time = time.time()
        
        # Draw grid background
        for x in range(COLS + 1):
            pygame.draw.line(self.screen, COLORS['tile_border'], 
                           (x * TILE_SIZE, 0), (x * TILE_SIZE, ROWS * TILE_SIZE))
        for y in range(ROWS + 1):
            pygame.draw.line(self.screen, COLORS['tile_border'], 
                           (0, y * TILE_SIZE), (COLS * TILE_SIZE, y * TILE_SIZE))
        
        # Draw tiles
        for y in range(ROWS):
            for x in range(COLS):
                tile = board[y][x]
                if tile != '-':
                    self.draw_tile(x, y, tile)
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()

    def die(self):
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

    def victory(self):
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

    def options(self):
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