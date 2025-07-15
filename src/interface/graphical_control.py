import random
import pygame
import time
import math
from typing import List, Tuple, Dict
from pathlib import Path
from ..agent.agent import Agent

# Constants
TILE_SIZE = 60
ROWS, COLS = 10, 10
BOARD_WIDTH, BOARD_HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE
UI_HEIGHT = 120
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 700

# Modern color palette
COLORS = {
    'background': (15, 20, 35),
    'background_gradient_top': (25, 35, 55),
    'background_gradient_bottom': (10, 15, 25),
    'tile_empty': (45, 52, 70),
    'tile_border': (70, 80, 100),
    'tile_highlight': (90, 100, 120),
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
    'ui_text': (220, 220, 220),
    'ui_text_highlight': (255, 255, 255),
    'ui_bg': (25, 30, 45),
    'ui_border': (60, 70, 90),
    'arrow': (255, 140, 0),
    'breeze': (100, 200, 255),
    'stench': (255, 100, 100),
    'trail': (100, 100, 100),
    'trail_glow': (150, 150, 150),
    'safe': (0, 100, 0, 50),
    'danger': (100, 0, 0, 50),
    'title_primary': (255, 255, 255),
    'title_secondary': (180, 180, 180),
    'title_glow': (100, 150, 255)
}

class WumpusGraphics:
    def __init__(self):
        pygame.init()
        self.window_width = pygame.display.Info().current_w
        self.window_height = pygame.display.Info().current_h
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
        pygame.display.set_caption("Wumpus World - AI Agent Adventure")
        self.clock = pygame.time.Clock()
        self.animation_time = time.time()
        self.particles = []
        
        # Calculate board position (centered)
        self.board_x = (self.window_width - BOARD_WIDTH) // 2
        self.board_y = (self.window_height - BOARD_HEIGHT - UI_HEIGHT) // 2 + 40 # 40px for title
        
        # Load fonts
        self.font_title = pygame.font.Font(None, 48)
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Load images
        self.images = self._load_images()
        
        # Background animation
        self.stars = [(pygame.math.Vector2(random.randint(0, self.window_width), 
                                         random.randint(0, self.window_height)), 
                      random.uniform(0.5, 2.0)) for _ in range(50)]

    def handle_resize(self, event):
        """Handle window resize while keeping board centered"""
        self.window_width = max(MIN_WINDOW_WIDTH, event.w)
        self.window_height = max(MIN_WINDOW_HEIGHT, event.h)
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
        
        # Recalculate board position
        self.board_x = (self.window_width - BOARD_WIDTH) // 2
        self.board_y = (self.window_height - BOARD_HEIGHT - UI_HEIGHT) // 2 + 40
        
        # Regenerate stars for new window size
        self.stars = [(pygame.math.Vector2(random.randint(0, self.window_width), 
                                         random.randint(0, self.window_height)), 
                      random.uniform(0.5, 2.0)) for _ in range(50)]

    def _draw_animated_background(self):
        """Draw animated starfield background"""
        # Gradient background
        for y in range(self.window_height):
            ratio = y / self.window_height
            r = int(COLORS['background_gradient_top'][0] * (1 - ratio) + COLORS['background_gradient_bottom'][0] * ratio)
            g = int(COLORS['background_gradient_top'][1] * (1 - ratio) + COLORS['background_gradient_bottom'][1] * ratio)
            b = int(COLORS['background_gradient_top'][2] * (1 - ratio) + COLORS['background_gradient_bottom'][2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.window_width, y))
        
        # Animated stars
        for i, (star_pos, speed) in enumerate(self.stars):
            # Move stars
            star_pos.x += speed * 0.5
            if star_pos.x > self.window_width:
                star_pos.x = -5
            
            # Twinkling effect
            brightness = int(255 * (0.5 + 0.5 * math.sin(self.animation_time * 3 + i * 0.5)))
            size = int(2 + math.sin(self.animation_time * 2 + i * 0.3))
            
            pygame.draw.circle(self.screen, (brightness, brightness, brightness), 
                             (int(star_pos.x), int(star_pos.y)), size)

    def _draw_title_bar(self):
        """Draw animated title bar"""
        title_y = 10
        
        # Title background with glow
        title_bg = pygame.Surface((self.window_width, 60), pygame.SRCALPHA)
        pygame.draw.rect(title_bg, (*COLORS['ui_bg'], 120), (0, 0, self.window_width, 60))
        self.screen.blit(title_bg, (0, title_y - 10))
        
        # Animated title text
        pulse = math.sin(self.animation_time * 2) * 0.1 + 0.9
        
        # Main title
        title_text = "WUMPUS WORLD"
        title_surface = self.font_title.render(title_text, True, COLORS['title_primary'])
        title_rect = title_surface.get_rect(center=(self.window_width // 2, title_y + 15))
        
        # Glow effect
        glow_surface = self.font_title.render(title_text, True, COLORS['title_glow'])
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_rect = glow_surface.get_rect(center=(title_rect.centerx + offset[0], title_rect.centery + offset[1]))
            glow_surface.set_alpha(int(50 * pulse))
            self.screen.blit(glow_surface, glow_rect)
        
        self.screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_text = "AI Agent Adventure"
        subtitle_surface = self.font_medium.render(subtitle_text, True, COLORS['title_secondary'])
        subtitle_rect = subtitle_surface.get_rect(center=(self.window_width // 2, title_y + 40))
        self.screen.blit(subtitle_surface, subtitle_rect)

    def _draw_enhanced_tile(self, x: int, y: int, tile_type: str) -> None:
        """Draw individual tile with enhanced graphics and animations"""
        pixel_x = self.board_x + x * TILE_SIZE
        pixel_y = self.board_y + y * TILE_SIZE
        center = (pixel_x + TILE_SIZE // 2, pixel_y + TILE_SIZE // 2)
        
        # Tile background with subtle animation
        tile_rect = pygame.Rect(pixel_x, pixel_y, TILE_SIZE, TILE_SIZE)
        
        # Add subtle hover-like effect
        hover_intensity = 0.5 + 0.5 * math.sin(self.animation_time * 1.5 + x * 0.3 + y * 0.5)
        base_color = COLORS['tile_empty']
        highlight_color = COLORS['tile_highlight']
        
        # Interpolate colors
        r = int(base_color[0] + (highlight_color[0] - base_color[0]) * hover_intensity * 0.1)
        g = int(base_color[1] + (highlight_color[1] - base_color[1]) * hover_intensity * 0.1)
        b = int(base_color[2] + (highlight_color[2] - base_color[2]) * hover_intensity * 0.1)
        
        pygame.draw.rect(self.screen, (r, g, b), tile_rect)
        pygame.draw.rect(self.screen, COLORS['tile_border'], tile_rect, 2)
        
        # Draw contents with image overlay if available
        if tile_type == 'A':
            self._draw_agent_enhanced(center)
        elif tile_type == 'W':
            self._draw_wumpus_enhanced(center)
        elif tile_type == 'B':
            self.draw_breeze(center)
        elif tile_type == 'S':
            self.draw_stench(center)
        elif tile_type == 'G':
            self._draw_gold_enhanced(center)
        elif tile_type == 'P':
            self.draw_pit(center)
        elif tile_type == '.':
            self.draw_trail(center)

    def _draw_agent_enhanced(self, center):
        """Enhanced agent drawing with image overlay"""
        self.draw_particle_trail(center, COLORS['player'])
        self.draw_glowing_circle(center, 18, COLORS['player'], COLORS['player_glow'])
        
        # Overlay image if available
        if 'player' in self.images:
            img = pygame.transform.scale(self.images['player'], (32, 32))
            img_rect = img.get_rect(center=center)
            self.screen.blit(img, img_rect)
        else:
            # Default drawing
            eye_pos = (center[0] + 5, center[1] - 5)
            pygame.draw.circle(self.screen, (255, 255, 255), eye_pos, 3)

    def _draw_wumpus_enhanced(self, center):
        """Enhanced Wumpus drawing with image overlay"""
        self.draw_pulsing_effect(center, 25, COLORS['wumpus_glow'])
        
        if 'wumpus' in self.images:
            # Scale and apply pulsing effect to image
            pulse = math.sin(self.animation_time * 3) * 0.1 + 0.9
            size = int(40 * pulse)
            img = pygame.transform.scale(self.images['wumpus'], (size, size))
            img_rect = img.get_rect(center=center)
            self.screen.blit(img, img_rect)
        else:
            # Default drawing
            self.draw_glowing_circle(center, 20, COLORS['wumpus'], COLORS['wumpus_glow'])
            eye1_pos = (center[0] - 6, center[1] - 8)
            eye2_pos = (center[0] + 6, center[1] - 8)
            pygame.draw.circle(self.screen, (255, 0, 0), eye1_pos, 3)
            pygame.draw.circle(self.screen, (255, 0, 0), eye2_pos, 3)

    def _draw_gold_enhanced(self, center):
        """Enhanced gold drawing with image overlay"""
        self.draw_pulsing_effect(center, 22, COLORS['gold_glow'])
        
        if 'gold' in self.images:
            # Rotating gold with sparkle effect
            angle = self.animation_time * 2
            img = pygame.transform.scale(self.images['gold'], (30, 30))
            rotated_img = pygame.transform.rotate(img, math.degrees(angle))
            img_rect = rotated_img.get_rect(center=center)
            self.screen.blit(rotated_img, img_rect)
        else:
            # Default diamond drawing
            diamond_points = [
                (center[0], center[1] - 15),
                (center[0] + 12, center[1]),
                (center[0], center[1] + 15),
                (center[0] - 12, center[1])
            ]
            pygame.draw.polygon(self.screen, COLORS['gold'], diamond_points)
            pygame.draw.polygon(self.screen, COLORS['gold_glow'], diamond_points, 2)
        
        # Sparkle effect
        for i in range(4):
            sparkle_x = center[0] + math.sin(self.animation_time * 4 + i * 1.5) * 25
            sparkle_y = center[1] + math.cos(self.animation_time * 4 + i * 1.5) * 25
            pygame.draw.circle(self.screen, (255, 255, 255), (int(sparkle_x), int(sparkle_y)), 2)

    def _draw_enhanced_ui(self, agent: Agent, status: str) -> None:
        """Enhanced UI with better styling"""
        ui_y = self.board_y + BOARD_HEIGHT + 20
        ui_width = BOARD_WIDTH
        ui_x = self.board_x
        
        # UI background with rounded corners effect
        ui_bg = pygame.Surface((ui_width, UI_HEIGHT - 20), pygame.SRCALPHA)
        pygame.draw.rect(ui_bg, COLORS['ui_bg'], (0, 0, ui_width, UI_HEIGHT - 20))
        pygame.draw.rect(ui_bg, COLORS['ui_border'], (0, 0, ui_width, UI_HEIGHT - 20), 2)
        self.screen.blit(ui_bg, (ui_x, ui_y))
        
        # Status with color coding
        status_color = COLORS['ui_text_highlight']
        if status == "Dead":
            status_color = COLORS['dead']
        elif status == "Victory":
            status_color = COLORS['victory']
        
        status_surf = self.font_large.render(f"Status: {status}", True, status_color)
        self.screen.blit(status_surf, (ui_x + 20, ui_y + 10))
        
        # Info panels
        info_items = [
            ("Position", f"{agent.position}", COLORS['ui_text']),
            ("Arrows", f"{agent.arrow_count}", COLORS['arrow']),
            ("Gold", f"{agent.gold_count}", COLORS['gold']),
            ("Score", f"{agent.score}", COLORS['ui_text_highlight'])
        ]
        
        panel_width = (ui_width - 60) // 4
        for i, (label, value, color) in enumerate(info_items):
            panel_x = ui_x + 20 + i * (panel_width + 10)
            panel_y = ui_y + 50
            
            # Mini panel background
            panel_bg = pygame.Surface((panel_width, 40), pygame.SRCALPHA)
            pygame.draw.rect(panel_bg, (*COLORS['tile_empty'], 180), (0, 0, panel_width, 40))
            self.screen.blit(panel_bg, (panel_x, panel_y))
            
            # Label
            label_surf = self.font_small.render(label, True, COLORS['ui_text'])
            label_rect = label_surf.get_rect(center=(panel_x + panel_width // 2, panel_y + 12))
            self.screen.blit(label_surf, label_rect)
            
            # Value
            value_surf = self.font_medium.render(value, True, color)
            value_rect = value_surf.get_rect(center=(panel_x + panel_width // 2, panel_y + 28))
            self.screen.blit(value_surf, value_rect)

    # ... (keeping all the existing drawing methods for breeze, stench, pit, etc.)
    
    def draw_glowing_circle(self, center, radius, color, glow_color):
        """Draw a circle with a glowing effect"""
        for i in range(5):
            alpha = 50 - i * 10
            if alpha > 0:
                glow_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*glow_color, alpha), (radius * 2, radius * 2), radius + i * 3)
                self.screen.blit(glow_surf, (center[0] - radius * 2, center[1] - radius * 2))
        
        pygame.draw.circle(self.screen, color, center, radius)

    def draw_pulsing_effect(self, center, base_radius, color, time_offset=0):
        """Draw a pulsing effect"""
        pulse = math.sin(self.animation_time * 3 + time_offset) * 0.3 + 0.7
        radius = int(base_radius * pulse)
        alpha = int(255 * pulse * 0.5)
        
        if alpha > 0:
            pulse_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(pulse_surf, (*color, alpha), (radius * 2, radius * 2), radius)
            self.screen.blit(pulse_surf, (center[0] - radius * 2, center[1] - radius * 2))

    def draw_particle_trail(self, center, color):
        """Draw trailing particles"""
        for i in range(8):
            offset_x = math.sin(self.animation_time * 2 + i * 0.8) * 15
            offset_y = math.cos(self.animation_time * 2 + i * 0.8) * 15
            alpha = int(255 * (1 - i / 8) * 0.3)
            
            if alpha > 0:
                particle_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, (*color, alpha), (3, 3), 3)
                self.screen.blit(particle_surf, (center[0] + offset_x - 3, center[1] + offset_y - 3))

    def draw_pit(self, center):
        """Draw a pit with dark swirling effect"""
        pygame.draw.circle(self.screen, COLORS['pit'], center, 15)
        
        for i in range(3):
            angle = self.animation_time * 2 + i * 2.1
            radius = 8 + i * 3
            swirl_x = center[0] + math.cos(angle) * radius
            swirl_y = center[1] + math.sin(angle) * radius
            pygame.draw.circle(self.screen, COLORS['pit_glow'], (int(swirl_x), int(swirl_y)), 3)

    def draw_breeze(self, center):
        """Draw breeze effect"""
        for i in range(3):
            angle = self.animation_time * 2 + i * 2.1
            radius = 15 + i * 5
            start_angle = angle
            end_angle = angle + 1.5
            
            pygame.draw.arc(self.screen, COLORS['breeze'], 
                          (center[0] - radius, center[1] - radius, radius * 2, radius * 2),
                          start_angle, end_angle, 3)
        
        for i in range(6):
            particle_angle = self.animation_time * 3 + i * 1.0
            particle_radius = 20 + math.sin(self.animation_time * 4 + i) * 5
            px = center[0] + math.cos(particle_angle) * particle_radius
            py = center[1] + math.sin(particle_angle) * particle_radius
            pygame.draw.circle(self.screen, COLORS['breeze'], (int(px), int(py)), 2)
        
        font = pygame.font.Font(None, 24)
        text = font.render("B", True, COLORS['breeze'])
        text_rect = text.get_rect(center=(center[0], center[1] + 25))
        self.screen.blit(text, text_rect)

    def draw_stench(self, center):
        """Draw stench effect"""
        for i in range(4):
            wave_offset = math.sin(self.animation_time * 4 + i * 0.5) * 3
            y_pos = center[1] - 20 + i * 10 + wave_offset
            
            points = []
            for x_offset in range(-20, 21, 4):
                wave_y = y_pos + math.sin((x_offset + self.animation_time * 50) * 0.3) * 2
                points.append((center[0] + x_offset, wave_y))
            
            if len(points) > 1:
                pygame.draw.lines(self.screen, COLORS['stench'], False, points, 2)
        
        skull_center = (center[0], center[1] - 5)
        pygame.draw.circle(self.screen, COLORS['stench'], skull_center, 8)
        
        pygame.draw.circle(self.screen, (0, 0, 0), (skull_center[0] - 3, skull_center[1] - 2), 2)
        pygame.draw.circle(self.screen, (0, 0, 0), (skull_center[0] + 3, skull_center[1] - 2), 2)
        
        font = pygame.font.Font(None, 24)
        text = font.render("S", True, COLORS['stench'])
        text_rect = text.get_rect(center=(center[0], center[1] + 25))
        self.screen.blit(text, text_rect)

    def draw_trail(self, center):
        """Draw a subtle dot to mark visited tiles"""
        pygame.draw.circle(self.screen, COLORS['trail'], center, 4)
        pygame.draw.circle(self.screen, COLORS['trail_glow'], center, 8, 2)
        
        pulse_radius = 6 + int(2 * math.sin(self.animation_time * 3))
        pygame.draw.circle(self.screen, COLORS['trail'], center, pulse_radius, 1)

    def _load_images(self) -> Dict[str, pygame.Surface]:
        """Load graphical assets if available and resize to cell size"""
        images = {}
        try:
            asset_path = Path("assets")
            if asset_path.exists():
                cell_size = TILE_SIZE
                gold_img = pygame.image.load(asset_path / "gold.png").convert_alpha()
                images['gold'] = pygame.transform.smoothscale(gold_img, (cell_size, cell_size))
                wumpus_img = pygame.image.load(asset_path / "wumpus.png").convert_alpha()
                images['wumpus'] = pygame.transform.smoothscale(wumpus_img, (cell_size, cell_size))
        except:
            print("Could not load images, using default rendering")
        return images

    def draw_board(self, board: List[List[str]], agent: Agent, status: str = "Exploring") -> None:
        """Main drawing method with enhanced graphics"""
        self.animation_time = time.time()
        
        # Draw animated background
        self._draw_animated_background()
        
        # Draw title bar
        self._draw_title_bar()
        
        # Draw board border with glow effect
        board_border = pygame.Rect(self.board_x - 5, self.board_y - 5, BOARD_WIDTH + 10, BOARD_HEIGHT + 10)
        pygame.draw.rect(self.screen, COLORS['ui_border'], board_border, 3)
        
        # Draw grid lines
        for x in range(COLS + 1):
            line_x = self.board_x + x * TILE_SIZE
            pygame.draw.line(self.screen, COLORS['tile_border'], 
                           (line_x, self.board_y), (line_x, self.board_y + BOARD_HEIGHT))
        for y in range(ROWS + 1):
            line_y = self.board_y + y * TILE_SIZE
            pygame.draw.line(self.screen, COLORS['tile_border'], 
                           (self.board_x, line_y), (self.board_x + BOARD_WIDTH, line_y))
        
        # Draw tiles
        for y in range(ROWS):
            for x in range(COLS):
                self._draw_enhanced_tile(x, y, board[y][x])
        
        # Draw enhanced UI
        self._draw_enhanced_ui(agent, status)
        
        pygame.display.flip()
        self.clock.tick(60)

    def animate_death(self):
        """Enhanced death animation"""
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        
        for frame in range(60):
            self.screen.blit(overlay, (0, 0))
            
            alpha = int(100 + 50 * math.sin(frame * 0.3))
            red_surf = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
            red_surf.fill((255, 0, 0, alpha))
            self.screen.blit(red_surf, (0, 0))
            
            death_text = self.font_title.render("GAME OVER", True, (255, 255, 255))
            text_rect = death_text.get_rect(center=(self.window_width//2, self.window_height//2))
            self.screen.blit(death_text, text_rect)
            
            pygame.display.flip()
            time.sleep(0.05)

    def animate_victory(self):
        """Enhanced victory animation"""
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.set_alpha(100)
        overlay.fill((255, 255, 255))
        
        for frame in range(90):
            self.screen.blit(overlay, (0, 0))
            
            for i in range(20):
                sparkle_x = (frame * 3 + i * 30) % self.window_width
                sparkle_y = 50 + 30 * math.sin(frame * 0.1 + i)
                pygame.draw.circle(self.screen, (255, 215, 0), (int(sparkle_x), int(sparkle_y)), 3)
            
            victory_text = self.font_title.render("VICTORY!", True, (50, 255, 50))
            text_rect = victory_text.get_rect(center=(self.window_width//2, self.window_height//2))
            self.screen.blit(victory_text, text_rect)
            
            pygame.display.flip()
            time.sleep(0.03)

    def display_options(self):
        """Enhanced options menu"""
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 30))
        self.screen.blit(overlay, (0, 0))
        
        panel_width = 400
        panel_height = 280
        panel_x = (self.window_width - panel_width) // 2
        panel_y = (self.window_height - panel_height) // 2
        
        # Enhanced panel with gradient
        panel_surface = pygame.Surface((panel_width, panel_height))
        for y in range(panel_height):
            ratio = y / panel_height
            r = int(45 * (1 - ratio) + 35 * ratio)
            g = int(50 * (1 - ratio) + 40 * ratio)
            b = int(65 * (1 - ratio) + 55 * ratio)
            pygame.draw.line(panel_surface, (r, g, b), (0, y), (panel_width, y))
        
        self.screen.blit(panel_surface, (panel_x, panel_y))
        pygame.draw.rect(self.screen, COLORS['ui_border'], (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Title with glow
        title_text = self.font_large.render("OPTIONS", True, COLORS['title_primary'])
        title_rect = title_text.get_rect(center=(self.window_width//2, panel_y + 50))
        self.screen.blit(title_text, title_rect)
        
        options = [
            ("Restart Game", "restart"),
            ("Take Snapshot", "snapshot"),
            ("Quit Game", "quit")
        ]
        
        option_rects = []
        mouse_pos = pygame.mouse.get_pos()
        
        for i, (option_text, action) in enumerate(options):
            option_y = panel_y + 110 + i * 50
            option_rect = pygame.Rect(panel_x + 30, option_y - 20, panel_width - 60, 40)
            option_rects.append(option_rect)
            
            is_hovered = option_rect.collidepoint(mouse_pos)
            
            if is_hovered:
                hover_surface = pygame.Surface((option_rect.width, option_rect.height))
                hover_surface.fill((70, 85, 110))
                self.screen.blit(hover_surface, option_rect)
                
                # Add glow effect for hovered option
                glow_surface = pygame.Surface((option_rect.width + 10, option_rect.height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*COLORS['title_glow'], 50), (0, 0, option_rect.width + 10, option_rect.height + 10))
                self.screen.blit(glow_surface, (option_rect.x - 5, option_rect.y - 5))
            
            # Draw option text with enhanced styling
            text_color = COLORS['title_primary'] if is_hovered else COLORS['ui_text']
            option_surface = self.font_medium.render(option_text, True, text_color)
            text_rect = option_surface.get_rect(center=option_rect.center)
            self.screen.blit(option_surface, text_rect)
        
        pygame.display.flip()
        
        # Handle events
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "close"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    for i, rect in enumerate(option_rects):
                        if rect.collidepoint(mouse_pos):
                            action = options[i][1]
                            if action == "snapshot":
                                pygame.image.save(self.screen, f"wumpus_snapshot_{int(time.time())}.png")
                                return "close"
                            return action
                elif event.type == pygame.MOUSEMOTION:
                    return self.display_options()
        
        return "close"

    def close(self) -> None:
        """Clean up resources"""
        pygame.quit()