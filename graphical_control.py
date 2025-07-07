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

class WumpusGame:
    def __init__(self, board_file='board.txt'):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Wumpus World - Enhanced Edition")
        
        # Load fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Game state
        self.board = self.load_board(board_file)
        self.player_pos = (9, 0)
        self.has_gold = False
        self.game_over = False
        self.victory_achieved = False
        self.animation_time = 0
        
        # Visual effects
        self.particle_effects = []
        
    def load_board(self, filename):
        try:
            with open(filename) as f:
                return [list(line.strip()) for line in f.readlines()]
        except FileNotFoundError:
            # Create a default board if file doesn't exist
            return [
                ['-', '-', '-', '-', 'W', '-', '-', '-', '-', '-'],
                ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                ['-', '-', '-', '-', '-', '-', 'G', '-', '-', '-'],
                ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                ['P', '-', '-', '-', '-', '-', '-', '-', '-', '-']
            ]

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

    def draw_board(self):
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
                tile = self.board[y][x]
                if tile != '-':
                    self.draw_tile(x, y, tile)
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()

    def move(self, dx, dy):
        if self.game_over or self.victory_achieved:
            return
            
        x, y = self.player_pos
        nx, ny = x + dx, y + dy
        
        if 0 <= nx < COLS and 0 <= ny < ROWS:
            # Check what's at the new position
            target_tile = self.board[ny][nx]
            
            # Clear current position
            self.board[y][x] = '-'
            
            # Handle special tiles
            if target_tile == 'W':
                self.die()
                return
            elif target_tile == 'G':
                self.has_gold = True
                
            # Move player
            self.player_pos = (nx, ny)
            self.board[ny][nx] = 'P'
            
            # Check for victory condition (return to start with gold)
            if self.has_gold and nx == 0 and ny == ROWS - 1:
                self.victory()
            
            self.draw_board()
            time.sleep(0.1)

    def move_up(self): self.move(0, -1)
    def move_down(self): self.move(0, 1)
    def move_left(self): self.move(-1, 0)
    def move_right(self): self.move(1, 0)

    def die(self):
        x, y = self.player_pos
        self.board[y][x] = 'X'
        self.game_over = True
        self.draw_board()
        time.sleep(1)

    def victory(self):
        x, y = self.player_pos
        self.board[y][x] = 'V'
        self.victory_achieved = True
        self.draw_board()
        time.sleep(1)

    def run(self):
        """Main game loop with keyboard controls"""
        running = True
        clock = pygame.time.Clock()
        
        self.draw_board()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.move_up()
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.move_down()
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.move_left()
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.move_right()
                    elif event.key == pygame.K_r and (self.game_over or self.victory_achieved):
                        # Restart game
                        self.__init__()
                        self.draw_board()
            
            # Redraw for animations
            if not self.game_over and not self.victory_achieved:
                self.draw_board()
            
            clock.tick(60)  # 60 FPS for smooth animations
        
        pygame.quit()


def main():
    game = WumpusGame('board.txt')
    game.run()


if __name__ == "__main__":
    main()