import pygame
import sys
import os
from RushHourPuzzle import RushHourPuzzle
from BFS import BFS
from AStar import AStar, h1, h2, h3
from Node import Node
import time

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 750

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rush Hour Puzzle Solver")

# Colour Palette:

COLORS = {
    'bg': (40, 44, 52),  # Dark background
    'bg_light': (58, 64, 77),  # Lighter dark
    'primary': (97, 175, 239),  # Blue
    'secondary': (224, 108, 117),  # Red
    'accent': (152, 195, 121),  # Green
    'warning': (229, 192, 123),  # Yellow
    'purple': (198, 120, 221),  # Purple
    'text': (255, 255, 255),  # White
    'text_dark': (171, 178, 191),  # Gray
    'border': (76, 82, 99),  # Border gray
    'X': (224, 108, 117),  # Red for target car
    'start': (229, 192, 123),  # Yellow for start
    'exit': (152, 195, 121),  # Green for exit
    'grid': (76, 82, 99),  # Grid color
    'wall': (76, 82, 99),  # Wall color
    'success': (152, 195, 121),  # Success green
}

# Vehicle colors organisés by its length and orientation
HORIZONTAL_COLORS = {
    2: (97, 175, 239),   # Blue for length 2
    3: (229, 192, 123),  # Yellow for 3
    4: (198, 120, 221),  # Purple for 4
}

VERTICAL_COLORS = {
    2: (152, 195, 121),  # Green for 2
    3: (209, 154, 102),  # Orange for 3
    4: (86, 182, 194),   # Cyan for 4
}


# Typography:

try:
    TITLE_FONT = pygame.font.Font(None, 84)
    SUBTITLE_FONT = pygame.font.Font(None, 48)
    BUTTON_FONT = pygame.font.Font(None, 36)
    TEXT_FONT = pygame.font.Font(None, 28)
    SMALL_FONT = pygame.font.Font(None, 22)
except:
    TITLE_FONT = pygame.font.Font(None, 84)
    SUBTITLE_FONT = pygame.font.Font(None, 48)
    BUTTON_FONT = pygame.font.Font(None, 36)
    TEXT_FONT = pygame.font.Font(None, 28)
    SMALL_FONT = pygame.font.Font(None, 22)

# Game states
STATE_WELCOME = "welcome"
STATE_ALGORITHM_SELECT = "algorithm_select"
STATE_FILE_SELECT = "file_select"
STATE_SOLVING = "solving"
STATE_ANIMATION = "animation"
STATE_COMPARISON = "comparison"



class Button:
    def __init__(self, x, y, width, height, text, color, hover_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color if hover_color else self._make_hover_color(color)
        self.current_color = color
        self.is_pressed = False
        self.is_hovered_flag = False
        
    def _make_hover_color(self, color):
        """We create a lighter version for the hover effect"""
        return tuple(min(255, c + 30) for c in color)
        
    def draw(self, surface):
        # Pixel art style button with border
        border_width = 3
        
        # Draw border (darker)
        border_rect = self.rect.inflate(border_width * 2, border_width * 2)
        pygame.draw.rect(surface, COLORS['border'], border_rect)
        
        # Draw button
        pygame.draw.rect(surface, self.current_color, self.rect)
        
        # Draw inner highlight (pixel art style) - only when not pressed
        if not self.is_pressed:
            highlight_rect = pygame.Rect(
                self.rect.x + 4, self.rect.y + 4,
                self.rect.width - 8, 2
            )
            lighter_color = tuple(min(255, c + 30) for c in self.current_color)
            pygame.draw.rect(surface, lighter_color, highlight_rect)
        
        # Draw outer glow when hovered
        if self.is_hovered_flag and not self.is_pressed:
            glow_rect = self.rect.inflate(6, 6)
            glow_color = tuple(min(255, c + 20) for c in self.current_color)
            pygame.draw.rect(surface, glow_color, glow_rect, 2)
        
        # Draw text
        text_surface = BUTTON_FONT.render(self.text, True, COLORS['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        if self.is_pressed:
            text_rect.y += 2
        surface.blit(text_surface, text_rect)
        
    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)
    
    def update(self, pos, mouse_pressed=False):
        self.is_hovered_flag = self.is_hovered(pos)
        if self.is_hovered_flag:
            self.current_color = self.hover_color
            self.is_pressed = mouse_pressed
        else:
            self.current_color = self.color
            self.is_pressed = False

class RushHourUI:
    def __init__(self):
        self.state = STATE_WELCOME
        self.selected_algorithm = None
        self.selected_file = None
        self.puzzle = None
        self.solution_path = []
        self.solution_actions = []
        self.current_step = 0
        self.animation_speed = 600  # milliseconds per step
        self.last_update = pygame.time.get_ticks()
        self.solving_time = 0
        self.vehicle_color_map = {}
        self.paused = False
        self.is_solving = False
        self.show_success = False
        self.waiting_dots = 0
        self.last_dot_update = pygame.time.get_ticks()
        
        # For comparison mode
        self.comparison_results = {}
        self.comparison_paths = {}  # Store solution paths for each algorithm
        self.comparison_steps = {}  # Current step for each algorithm
        self.comparison_solving = False
        
        # Available example files
        self.example_files = [
            "examples/1.csv",
            "examples/2-a.csv",
            "examples/2-b.csv",
            "examples/2-c.csv",
            "examples/2-d.csv",
            "examples/2-e.csv",
        ]
        
        # Buttons for welcome screen
        self.start_button = Button(
            SCREEN_WIDTH // 2 - 180, 550, 360, 80,
            "START GAME", COLORS['accent']
        )
        
        # Algorithm selection buttons
        button_width = 450
        button_height = 65
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_spacing = 80
        start_y = 280
        
        self.bfs_button = Button(
            button_x, start_y, button_width, button_height,
            "BFS - Breadth First Search", COLORS['primary']
        )
        self.astar_h1_button = Button(
            button_x, start_y + button_spacing, button_width, button_height,
            "A* with h1 (Simple Distance)", COLORS['warning']
        )
        self.astar_h2_button = Button(
            button_x, start_y + button_spacing * 2, button_width, button_height,
            "A* with h2 (With Blocking)", COLORS['accent']
        )
        self.astar_h3_button = Button(
            button_x, start_y + button_spacing * 3, button_width, button_height,
            "A* with h3 (Advanced)", COLORS['purple']
        )
        self.compare_button = Button(
            button_x, start_y + button_spacing * 4, button_width, button_height,
            "COMPARE ALL ALGORITHMS", COLORS['secondary']
        )
        
        # File selection buttons
        self.file_buttons = []
        file_button_width = 300
        file_button_height = 60
        file_start_x = SCREEN_WIDTH // 2 - file_button_width // 2
        file_start_y = 250
        file_spacing = 75
        
        for i, file_path in enumerate(self.example_files):
            file_name = os.path.basename(file_path).replace('.csv', '')
            btn = Button(
                file_start_x, file_start_y + i * file_spacing,
                file_button_width, file_button_height,
                f"Puzzle {file_name}", COLORS['bg_light']
            )
            self.file_buttons.append(btn)
        
        # Control buttons
        self.back_button = Button(30, 30, 120, 50, "BACK", COLORS['text_dark'])
        self.pause_button = Button(SCREEN_WIDTH - 160, 30, 130, 50, "PAUSE", COLORS['warning'])
        self.restart_button = Button(SCREEN_WIDTH - 160, 90, 130, 50, "RESTART", COLORS['secondary'])
        
        # Success popup button
        self.continue_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, 200, 60,
            "CONTINUE", COLORS['success']
        )
        
    def draw_pixel_car(self, surface, x, y, width, height, color, is_horizontal=True):
        """Draw a simple pixel art car"""
        # Main body
        pygame.draw.rect(surface, color, (x, y, width, height))
        
        # Add highlights (pixel art style)
        lighter_color = tuple(min(255, c + 40) for c in color)
        darker_color = tuple(max(0, c - 40) for c in color)
        
        # Top highlight
        pygame.draw.rect(surface, lighter_color, (x + 2, y + 2, width - 4, 3))
        
        # Bottom shadow
        pygame.draw.rect(surface, darker_color, (x + 2, y + height - 5, width - 4, 3))
        
        # Draw windows based on orientation
        window_color = COLORS['bg']
        if is_horizontal:
            if width > 40:  # Only draw windows if car is long enough
                # Front window
                pygame.draw.rect(surface, window_color, 
                               (x + width - 15, y + height // 4, 8, height // 2))
                # Back window
                pygame.draw.rect(surface, window_color,
                               (x + 5, y + height // 4, 8, height // 2))
        else:
            if height > 40:  # Only draw windows if car is long enough
                # Front window
                pygame.draw.rect(surface, window_color,
                               (x + width // 4, y + 5, width // 2, 8))
                # Back window
                pygame.draw.rect(surface, window_color,
                               (x + width // 4, y + height - 13, width // 2, 8))
        
    def draw_welcome_screen(self):
        screen.fill(COLORS['bg'])
        
        # Draw pixel art grid pattern in background
        grid_size = 40
        for x in range(0, SCREEN_WIDTH, grid_size):
            pygame.draw.line(screen, COLORS['bg_light'], (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, grid_size):
            pygame.draw.line(screen, COLORS['bg_light'], (0, y), (SCREEN_WIDTH, y), 1)
        
        # Title with pixel art style
        title_text = TITLE_FONT.render("RUSH HOUR GAME SOLVER", True, COLORS['text'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
        
        # Draw title border (pixel art shadow)
        shadow_text = TITLE_FONT.render("RUSH HOUR GAME SOLVER", True, COLORS['border'])
        screen.blit(shadow_text, (title_rect.x + 4, title_rect.y + 4))
        screen.blit(title_text, title_rect)
        
        # Draw decorative pixel art cars
        # Red car (X car) at top
        self.draw_pixel_car(screen, SCREEN_WIDTH // 2 - 60, 150, 120, 40, COLORS['X'], True)
        
        # Blue horizontal car left side
        self.draw_pixel_car(screen, 200, 380, 100, 35, HORIZONTAL_COLORS[2], True)
        
        # Yellow horizontal car right side
        self.draw_pixel_car(screen, SCREEN_WIDTH - 300, 380, 100, 35, HORIZONTAL_COLORS[3], True)
        
        # Green vertical car left
        self.draw_pixel_car(screen, 350, 320, 35, 80, VERTICAL_COLORS[2], False)
        
        # Orange vertical car right
        self.draw_pixel_car(screen, SCREEN_WIDTH - 385, 320, 35, 80, VERTICAL_COLORS[3], False)
        
        # Purple car center bottom
        self.draw_pixel_car(screen, SCREEN_WIDTH // 2 - 50, 420, 100, 35, HORIZONTAL_COLORS[4], True)
        
        # Draw start button
        self.start_button.draw(screen)
        
    def draw_algorithm_select_screen(self):
        screen.fill(COLORS['bg'])
        
        # Draw back button
        self.back_button.draw(screen)
        
        # Title
        title_text = TITLE_FONT.render("SELECT ALGORITHM", True, COLORS['text'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        
        # Draw title with pixel border
        shadow_text = TITLE_FONT.render("SELECT ALGORITHM", True, COLORS['border'])
        screen.blit(shadow_text, (title_rect.x + 3, title_rect.y + 3))
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = TEXT_FONT.render("Choose a search algorithm to solve the puzzle", True, COLORS['text_dark'])
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Draw algorithm buttons with proper spacing
        self.bfs_button.draw(screen)
        self.astar_h1_button.draw(screen)
        self.astar_h2_button.draw(screen)
        self.astar_h3_button.draw(screen)
        self.compare_button.draw(screen)
        
    def draw_file_select_screen(self):
        screen.fill(COLORS['bg'])
        
        # Draw back button
        self.back_button.draw(screen)
        
        # Title
        title_text = TITLE_FONT.render("SELECT PUZZLE", True, COLORS['text'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        
        shadow_text = TITLE_FONT.render("SELECT PUZZLE", True, COLORS['border'])
        screen.blit(shadow_text, (title_rect.x + 3, title_rect.y + 3))
        screen.blit(title_text, title_rect)
        
        # Subtitle
        algo_names = {
            'bfs': 'BFS',
            'h1': 'A* (h1)',
            'h2': 'A* (h2)',
            'h3': 'A* (h3)',
            'compare': 'Comparison Mode'
        }
        algo_name = algo_names.get(self.selected_algorithm, 'Unknown')
        
        subtitle_text = TEXT_FONT.render(f"Algorithm: {algo_name}", True, COLORS['accent'])
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Draw file selection buttons
        for btn in self.file_buttons:
            btn.draw(screen)
    
    def assign_vehicle_colors(self, vehicles):
        """Assign colours based on car's length and orientation"""
        for vehicle in vehicles:
            vid = vehicle['id']
            if vid == 'X':
                # Red car is always red
                self.vehicle_color_map[vid] = COLORS['X']
            elif vid not in self.vehicle_color_map:
                # Assign color based on orientation and length
                length = vehicle['length']
                orientation = vehicle['orientation']
                
                if orientation == 'H':
                    # Horizontal vehicles
                    self.vehicle_color_map[vid] = HORIZONTAL_COLORS.get(length, HORIZONTAL_COLORS[2])
                else:
                    # Vertical vehicles
                    self.vehicle_color_map[vid] = VERTICAL_COLORS.get(length, VERTICAL_COLORS[2])
    
    def draw_board(self, state, x_offset, y_offset, cell_size=70):
        """Draw the Rush Hour board in pixel art style"""
        board_width = state.board_width
        board_height = state.board_height
        
        # Draw board background with pixel border
        board_rect = pygame.Rect(
            x_offset - 8, y_offset - 8,
            board_width * cell_size + 16,
            board_height * cell_size + 16
        )
        pygame.draw.rect(screen, COLORS['border'], board_rect)
        
        inner_rect = pygame.Rect(
            x_offset, y_offset,
            board_width * cell_size,
            board_height * cell_size
        )
        pygame.draw.rect(screen, COLORS['bg_light'], inner_rect)
        
        # Draw START indicator (pixel art arrow) - on the left side
        start_row = board_height // 2 - 1
        start_x = x_offset - 80
        start_y = y_offset + start_row * cell_size + cell_size // 2
        
        # Draw start label
        start_text = SMALL_FONT.render("START", True, COLORS['start'])
        screen.blit(start_text, (start_x, start_y - 30))
        
        # Draw arrow pointing right (pixel art style)
        start_arrow_points = [
            (start_x + 50, start_y),
            (start_x + 30, start_y - 10),
            (start_x + 30, start_y + 10)
        ]
        pygame.draw.polygon(screen, COLORS['start'], start_arrow_points)
        
        # Draw exit indicator (pixel art arrow)
        exit_row = board_height // 2 - 1
        exit_x = x_offset + board_width * cell_size + 15
        exit_y = y_offset + exit_row * cell_size + cell_size // 2
        
        # Draw exit label
        exit_text = SMALL_FONT.render("EXIT", True, COLORS['exit'])
        screen.blit(exit_text, (exit_x, exit_y - 30))
        
        # Draw arrow (pixel art style)
        arrow_points = [
            (exit_x, exit_y),
            (exit_x + 20, exit_y - 10),
            (exit_x + 20, exit_y + 10)
        ]
        pygame.draw.polygon(screen, COLORS['exit'], arrow_points)
        
        # Draw grid (pixel art style)
        for row in range(board_height + 1):
            y = y_offset + row * cell_size
            pygame.draw.line(screen, COLORS['grid'],
                           (x_offset, y),
                           (x_offset + board_width * cell_size, y), 2)
        for col in range(board_width + 1):
            x = x_offset + col * cell_size
            pygame.draw.line(screen, COLORS['grid'],
                           (x, y_offset),
                           (x, y_offset + board_height * cell_size), 2)
        
        # Draw walls (obstacles) with pixel art style
        if hasattr(state, 'walls') and state.walls:
            for wall_x, wall_y in state.walls:
                wall_rect = pygame.Rect(
                    x_offset + wall_x * cell_size + 4,
                    y_offset + wall_y * cell_size + 4,
                    cell_size - 8,
                    cell_size - 8
                )
                
                # Draw wall with brick pattern
                # Base color - dark gray
                pygame.draw.rect(screen, (60, 60, 60), wall_rect)
                
                # Draw brick lines (pixel art style)
                brick_color = (80, 80, 80)
                # Horizontal lines
                pygame.draw.line(screen, brick_color,
                               (wall_rect.x, wall_rect.y + wall_rect.height // 3),
                               (wall_rect.x + wall_rect.width, wall_rect.y + wall_rect.height // 3), 2)
                pygame.draw.line(screen, brick_color,
                               (wall_rect.x, wall_rect.y + 2 * wall_rect.height // 3),
                               (wall_rect.x + wall_rect.width, wall_rect.y + 2 * wall_rect.height // 3), 2)
                
                # Vertical lines offset for brick pattern
                pygame.draw.line(screen, brick_color,
                               (wall_rect.x + wall_rect.width // 2, wall_rect.y),
                               (wall_rect.x + wall_rect.width // 2, wall_rect.y + wall_rect.height // 3), 2)
                pygame.draw.line(screen, brick_color,
                               (wall_rect.x + wall_rect.width // 3, wall_rect.y + wall_rect.height // 3),
                               (wall_rect.x + wall_rect.width // 3, wall_rect.y + 2 * wall_rect.height // 3), 2)
                pygame.draw.line(screen, brick_color,
                               (wall_rect.x + 2 * wall_rect.width // 3, wall_rect.y + wall_rect.height // 3),
                               (wall_rect.x + 2 * wall_rect.width // 3, wall_rect.y + 2 * wall_rect.height // 3), 2)
                pygame.draw.line(screen, brick_color,
                               (wall_rect.x + wall_rect.width // 2, wall_rect.y + 2 * wall_rect.height // 3),
                               (wall_rect.x + wall_rect.width // 2, wall_rect.y + wall_rect.height), 2)
                
                # Border
                pygame.draw.rect(screen, COLORS['border'], wall_rect, 3)
                
                # Draw # symbol on wall
                wall_text = TEXT_FONT.render("#", True, (100, 100, 100))
                wall_text_rect = wall_text.get_rect(center=wall_rect.center)
                screen.blit(wall_text, wall_text_rect)
        
        # Draw vehicles with pixel art style
        for vehicle in state.vehicles:
            vid = vehicle['id']
            x = vehicle['x']
            y = vehicle['y']
            length = vehicle['length']
            orientation = vehicle['orientation']
            
            color = self.vehicle_color_map.get(vid, COLORS['primary'])
            
            if orientation == 'H':
                car_x = x_offset + x * cell_size + 8
                car_y = y_offset + y * cell_size + 8
                car_width = length * cell_size - 16
                car_height = cell_size - 16
                self.draw_pixel_car(screen, car_x, car_y, car_width, car_height, color, True)
            else:
                car_x = x_offset + x * cell_size + 8
                car_y = y_offset + y * cell_size + 8
                car_width = cell_size - 16
                car_height = length * cell_size - 16
                self.draw_pixel_car(screen, car_x, car_y, car_width, car_height, color, False)
            
            # Draw vehicle ID with pixel font
            text = TEXT_FONT.render(vid, True, COLORS['text'])
            text_rect = text.get_rect(center=(car_x + car_width // 2, car_y + car_height // 2))
            screen.blit(text, text_rect)
    
    def draw_animation_screen(self):
        screen.fill(COLORS['bg'])
        
        # Show waiting indicator if solving
        if self.is_solving:
            self.draw_waiting_indicator()
            return
        
        # Draw control buttons
        self.back_button.draw(screen)
        self.pause_button.draw(screen)
        self.restart_button.draw(screen)
        
        # Algorithm name and info panel (left side)
        algo_names = {
            'bfs': 'BFS Algorithm',
            'h1': 'A* with h1',
            'h2': 'A* with h2',
            'h3': 'A* with h3'
        }
        algo_name = algo_names.get(self.selected_algorithm, 'Unknown')
        
        # Info panel background
        panel_rect = pygame.Rect(30, 100, 350, 400)
        pygame.draw.rect(screen, COLORS['bg_light'], panel_rect)
        pygame.draw.rect(screen, COLORS['border'], panel_rect, 3)
        
        # Title in panel
        title_text = SUBTITLE_FONT.render(algo_name, True, COLORS['text'])
        screen.blit(title_text, (50, 120))
        
        # Draw puzzle file name
        if self.selected_file:
            file_name = os.path.basename(self.selected_file)
            file_text = TEXT_FONT.render(f"Puzzle: {file_name}", True, COLORS['text_dark'])
            screen.blit(file_text, (50, 170))
        
        # Stats
        if self.solution_path:
            stats_y = 220
            stats = [
                ("Total Moves", f"{len(self.solution_path) - 1}"),
                ("Current Step", f"{self.current_step + 1} / {len(self.solution_path)}"),
                ("Solve Time", f"{self.solving_time:.3f}s"),
            ]
            
            for label, value in stats:
                label_text = SMALL_FONT.render(label + ":", True, COLORS['text_dark'])
                screen.blit(label_text, (50, stats_y))
                
                value_text = TEXT_FONT.render(value, True, COLORS['accent'])
                screen.blit(value_text, (50, stats_y + 22))
                
                stats_y += 60
            
            # Current action
            if self.current_step > 0 and self.solution_actions:
                action_y = 420
                action_label = SMALL_FONT.render("Current Action:", True, COLORS['text_dark'])
                screen.blit(action_label, (50, action_y))
                
                action = self.solution_actions[self.current_step - 1]
                directions = {'L': 'LEFT', 'R': 'RIGHT', 'U': 'UP', 'D': 'DOWN'}
                action_text = TEXT_FONT.render(
                    f"{action[0]} -> {directions.get(action[1], action[1])}",
                    True, COLORS['warning']
                )
                screen.blit(action_text, (50, action_y + 25))
        
        # Draw board (right side, larger and centered better)
        if self.solution_path and self.current_step < len(self.solution_path):
            current_state = self.solution_path[self.current_step]
            board_x = 500
            board_y = 150
            self.draw_board(current_state, board_x, board_y, 80)
        
        # Progress bar at bottom
        if self.solution_path:
            bar_width = 800
            bar_height = 30
            bar_x = (SCREEN_WIDTH - bar_width) // 2
            bar_y = SCREEN_HEIGHT - 80
            
            # Background
            pygame.draw.rect(screen, COLORS['bg_light'], (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, COLORS['border'], (bar_x, bar_y, bar_width, bar_height), 3)
            
            # Progress
            progress = (self.current_step + 1) / len(self.solution_path)
            progress_width = int((bar_width - 6) * progress)
            pygame.draw.rect(screen, COLORS['accent'], 
                           (bar_x + 3, bar_y + 3, progress_width, bar_height - 6))
            
            # Percentage text
            percent_text = TEXT_FONT.render(f"{int(progress * 100)}%", True, COLORS['text'])
            percent_rect = percent_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
            screen.blit(percent_text, percent_rect)
        
        # Draw success popup if finished
        if self.show_success:
            self.draw_success_popup()
    
    def draw_waiting_indicator(self):
        """Draw animated waiting screen while algorithm is solving"""
        screen.fill(COLORS['bg'])
        
        # Update dots animation
        current_time = pygame.time.get_ticks()
        if current_time - self.last_dot_update > 500:
            self.waiting_dots = (self.waiting_dots + 1) % 4
            self.last_dot_update = current_time
        
        # Main message
        message = "Solving puzzle"
        dots = "." * self.waiting_dots
        full_message = message + dots
        
        message_text = TITLE_FONT.render(full_message, True, COLORS['text'])
        message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(message_text, message_rect)
        
        # Subtitle
        subtitle_text = SUBTITLE_FONT.render("Wait for the magic to happen...", True, COLORS['text_dark'])
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Animated spinner (pixel art style)
        spinner_x = SCREEN_WIDTH // 2
        spinner_y = SCREEN_HEIGHT // 2 + 100
        spinner_size = 40
        angle = (pygame.time.get_ticks() // 50) % 360
        
        for i in range(8):
            a = angle + i * 45
            end_x = spinner_x + int(spinner_size * pygame.math.Vector2(1, 0).rotate(a).x)
            end_y = spinner_y + int(spinner_size * pygame.math.Vector2(1, 0).rotate(a).y)
            alpha = 255 - i * 30
            color = tuple(max(0, c - i * 20) for c in COLORS['accent'][:3])
            pygame.draw.circle(screen, color, (end_x, end_y), 6)
    
    def draw_success_popup(self):
        """Draw success popup when puzzle is solved"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Popup box
        popup_width = 500
        popup_height = 300
        popup_x = (SCREEN_WIDTH - popup_width) // 2
        popup_y = (SCREEN_HEIGHT - popup_height) // 2
        
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        
        # Draw border
        border_rect = popup_rect.inflate(8, 8)
        pygame.draw.rect(screen, COLORS['success'], border_rect)
        pygame.draw.rect(screen, COLORS['bg'], popup_rect)
        
        # Success title
        success_text = TITLE_FONT.render("SUCCESS!", True, COLORS['success'])
        success_rect = success_text.get_rect(center=(SCREEN_WIDTH // 2, popup_y + 70))
        screen.blit(success_text, success_rect)
        
        # Stats
        if self.solution_path:
            moves_text = SUBTITLE_FONT.render(
                f"Solved in {len(self.solution_path) - 1} moves",
                True, COLORS['text']
            )
            moves_rect = moves_text.get_rect(center=(SCREEN_WIDTH // 2, popup_y + 140))
            screen.blit(moves_text, moves_rect)
            
            time_text = TEXT_FONT.render(
                f"Time: {self.solving_time:.3f}s",
                True, COLORS['text_dark']
            )
            time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, popup_y + 180))
            screen.blit(time_text, time_rect)
        
        # Continue button
        self.continue_button.draw(screen)
    
    def draw_comparison_screen(self):
        screen.fill(COLORS['bg'])
        
        # Draw back button
        self.back_button.draw(screen)
        
        # Title
        title_text = TITLE_FONT.render("COMPARISON MODE", True, COLORS['text'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        shadow_text = TITLE_FONT.render("COMPARISON MODE", True, COLORS['border'])
        screen.blit(shadow_text, (title_rect.x + 3, title_rect.y + 3))
        screen.blit(title_text, title_rect)
        
        # Show waiting indicator while comparing
        if self.comparison_solving:
            # Update dots animation
            current_time = pygame.time.get_ticks()
            if current_time - self.last_dot_update > 500:
                self.waiting_dots = (self.waiting_dots + 1) % 4
                self.last_dot_update = current_time
            
            # Main message
            message = "Comparing algorithms"
            dots = "." * self.waiting_dots
            full_message = message + dots
            
            message_text = SUBTITLE_FONT.render(full_message, True, COLORS['text'])
            message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(message_text, message_rect)
            
            # Subtitle
            subtitle_text = TEXT_FONT.render("Running BFS, A* h1, A* h2, A* h3", True, COLORS['text_dark'])
            subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            screen.blit(subtitle_text, subtitle_rect)
            
            # Animated spinner (pixel art style)
            spinner_x = SCREEN_WIDTH // 2
            spinner_y = SCREEN_HEIGHT // 2 + 100
            spinner_size = 40
            angle = (pygame.time.get_ticks() // 50) % 360
            
            for i in range(8):
                a = angle + i * 45
                end_x = spinner_x + int(spinner_size * pygame.math.Vector2(1, 0).rotate(a).x)
                end_y = spinner_y + int(spinner_size * pygame.math.Vector2(1, 0).rotate(a).y)
                color = tuple(max(0, c - i * 20) for c in COLORS['accent'][:3])
                pygame.draw.circle(screen, color, (end_x, end_y), 6)
        
        # Show comparison results when done
        elif hasattr(self, 'comparison_results') and self.comparison_results:
            y_offset = 200
            col_widths = [300, 150, 150]
            
            # Header
            headers = ["Algorithm", "Moves", "Time (s)"]
            x = 200
            for i, header in enumerate(headers):
                text = SUBTITLE_FONT.render(header, True, COLORS['accent'])
                screen.blit(text, (x, y_offset))
                x += col_widths[i]
            
            y_offset += 70
            
            # Results
            for algo, result in self.comparison_results.items():
                x = 200
                
                # Algorithm name
                algo_text = TEXT_FONT.render(algo, True, COLORS['text'])
                screen.blit(algo_text, (x, y_offset))
                x += col_widths[0]
                
                # Moves
                moves_text = TEXT_FONT.render(str(result['moves']), True, COLORS['text'])
                screen.blit(moves_text, (x, y_offset))
                x += col_widths[1]
                
                # Time
                time_text = TEXT_FONT.render(f"{result['time']:.3f}", True, COLORS['text'])
                screen.blit(time_text, (x, y_offset))
                
                y_offset += 50
    
    def solve_puzzle(self, algorithm):
        """Solve the puzzle with selected algorithm"""
        if not self.selected_file:
            return False
        
        self.is_solving = True
        self.puzzle = RushHourPuzzle(self.selected_file)
        self.assign_vehicle_colors(self.puzzle.vehicles)
        
        start_time = time.time()
        
        if algorithm == 'bfs':
            goal_node = BFS(
                self.puzzle,
                lambda state: state.successorFunction(),
                lambda state: state.isGoal()
            )
        else:
            heuristic = {'h1': h1, 'h2': h2, 'h3': h3}[algorithm]
            goal_node = AStar(
                self.puzzle,
                lambda state: state.successorFunction(),
                lambda state: state.isGoal(),
                heuristic
            )
        
        self.solving_time = time.time() - start_time
        self.is_solving = False
        
        if goal_node:
            self.solution_path = goal_node.getPath()
            self.solution_actions = goal_node.getSolution()
            self.current_step = 0
            return True
        return False
    
    def compare_all_algorithms(self):
        """Compare all algorithms on selected puzzle"""
        if not self.selected_file:
            return
        
        self.comparison_results = {}
        
        algorithms = [
            ('BFS', 'bfs', None),
            ('A* h1', 'h1', h1),
            ('A* h2', 'h2', h2),
            ('A* h3', 'h3', h3)
        ]
        
        for name, algo_key, heuristic in algorithms:
            puzzle = RushHourPuzzle(self.selected_file)
            start_time = time.time()
            
            if algo_key == 'bfs':
                goal_node = BFS(
                    puzzle,
                    lambda state: state.successorFunction(),
                    lambda state: state.isGoal()
                )
            else:
                goal_node = AStar(
                    puzzle,
                    lambda state: state.successorFunction(),
                    lambda state: state.isGoal(),
                    heuristic
                )
            
            solve_time = time.time() - start_time
            
            if goal_node:
                self.comparison_results[name] = {
                    'moves': len(goal_node.getSolution()),
                    'time': solve_time
                }
        
        # Mark comparison as complete
        self.comparison_solving = False
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == STATE_WELCOME:
                        if self.start_button.is_hovered(mouse_pos):
                            self.state = STATE_ALGORITHM_SELECT
                    
                    elif self.state == STATE_ALGORITHM_SELECT:
                        if self.back_button.is_hovered(mouse_pos):
                            self.state = STATE_WELCOME
                        elif self.bfs_button.is_hovered(mouse_pos):
                            self.selected_algorithm = 'bfs'
                            self.state = STATE_FILE_SELECT
                        elif self.astar_h1_button.is_hovered(mouse_pos):
                            self.selected_algorithm = 'h1'
                            self.state = STATE_FILE_SELECT
                        elif self.astar_h2_button.is_hovered(mouse_pos):
                            self.selected_algorithm = 'h2'
                            self.state = STATE_FILE_SELECT
                        elif self.astar_h3_button.is_hovered(mouse_pos):
                            self.selected_algorithm = 'h3'
                            self.state = STATE_FILE_SELECT
                        elif self.compare_button.is_hovered(mouse_pos):
                            self.selected_algorithm = 'compare'
                            self.state = STATE_FILE_SELECT
                    
                    elif self.state == STATE_FILE_SELECT:
                        if self.back_button.is_hovered(mouse_pos):
                            self.state = STATE_ALGORITHM_SELECT
                        else:
                            for i, btn in enumerate(self.file_buttons):
                                if btn.is_hovered(mouse_pos):
                                    self.selected_file = self.example_files[i]
                                    
                                    if self.selected_algorithm == 'compare':
                                        self.state = STATE_COMPARISON
                                        self.comparison_solving = True
                                        self.comparison_results = {}
                                        # Comparison will run in the main loop
                                    else:
                                        # Set solving state to show waiting indicator
                                        self.state = STATE_SOLVING
                                        self.is_solving = True
                                        # Solving will run in the main loop
                                    break
                    
                    elif self.state == STATE_ANIMATION:
                        if self.back_button.is_hovered(mouse_pos):
                            self.state = STATE_FILE_SELECT
                            self.current_step = 0
                            self.paused = False
                            self.show_success = False
                        elif self.pause_button.is_hovered(mouse_pos):
                            self.paused = not self.paused
                            self.pause_button.text = "PLAY" if self.paused else "PAUSE"
                        elif self.restart_button.is_hovered(mouse_pos):
                            self.current_step = 0
                            self.paused = False
                            self.show_success = False
                            self.last_update = pygame.time.get_ticks()
                        elif self.show_success and self.continue_button.is_hovered(mouse_pos):
                            self.show_success = False
                            self.state = STATE_FILE_SELECT
                    
                    elif self.state == STATE_COMPARISON:
                        if self.back_button.is_hovered(mouse_pos):
                            self.state = STATE_FILE_SELECT
            
            # Update button hover states
            if self.state == STATE_WELCOME:
                self.start_button.update(mouse_pos, mouse_pressed)
            elif self.state == STATE_ALGORITHM_SELECT:
                self.back_button.update(mouse_pos, mouse_pressed)
                self.bfs_button.update(mouse_pos, mouse_pressed)
                self.astar_h1_button.update(mouse_pos, mouse_pressed)
                self.astar_h2_button.update(mouse_pos, mouse_pressed)
                self.astar_h3_button.update(mouse_pos, mouse_pressed)
                self.compare_button.update(mouse_pos, mouse_pressed)
            elif self.state == STATE_FILE_SELECT:
                self.back_button.update(mouse_pos, mouse_pressed)
                for btn in self.file_buttons:
                    btn.update(mouse_pos, mouse_pressed)
            elif self.state == STATE_ANIMATION:
                self.back_button.update(mouse_pos, mouse_pressed)
                self.pause_button.update(mouse_pos, mouse_pressed)
                self.restart_button.update(mouse_pos, mouse_pressed)
                if self.show_success:
                    self.continue_button.update(mouse_pos, mouse_pressed)
            elif self.state == STATE_COMPARISON:
                self.back_button.update(mouse_pos, mouse_pressed)
            
            # Animation logic
            if self.state == STATE_ANIMATION and self.solution_path and not self.paused and not self.is_solving:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_update > self.animation_speed:
                    if self.current_step < len(self.solution_path) - 1:
                        self.current_step += 1
                    else:
                        # Reached the end, show success popup
                        self.show_success = True
                    self.last_update = current_time
            
            # Draw current state
            if self.state == STATE_WELCOME:
                self.draw_welcome_screen()
            elif self.state == STATE_ALGORITHM_SELECT:
                self.draw_algorithm_select_screen()
            elif self.state == STATE_FILE_SELECT:
                self.draw_file_select_screen()
            elif self.state == STATE_SOLVING:
                self.draw_waiting_indicator()
            elif self.state == STATE_ANIMATION:
                self.draw_animation_screen()
            elif self.state == STATE_COMPARISON:
                self.draw_comparison_screen()
            
            # Update display before potentially blocking operation
            pygame.display.flip()
            clock.tick(60)
            
            # Run single algorithm solving AFTER drawing waiting indicator
            if self.state == STATE_SOLVING and self.is_solving:
                if self.solve_puzzle(self.selected_algorithm):
                    self.state = STATE_ANIMATION
                    self.last_update = pygame.time.get_ticks()
                else:
                    self.state = STATE_FILE_SELECT
                # Skip the display update at the end since we already did it
                continue
            
            # Run comparison AFTER drawing waiting indicator
            if self.state == STATE_COMPARISON and self.comparison_solving:
                self.compare_all_algorithms()
                # Skip the display update at the end since we already did it
                continue
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = RushHourUI()
    game.run()
