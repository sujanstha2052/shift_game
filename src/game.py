import sys
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    TILE_SIZE,
    FPS,
    TITLE,
    COLOR_GRID_LINE,
    COLOR_TEXT,
)
from src.level import Level
from src.player import Player
from src.levels_data import LEVELS


class Game:
    """
    The Game class manages the game lifecycle:
    - Setting up the window and Pygame clock
    - Holding the current level and player state
    - Running the main loop (events -> update -> draw)
    """

    def __init__(self):
        # 1. Initialize Pygame subsystems
        pygame.init()
        pygame.font.init()

        # 2. Setup display window & title
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)

        # 3. Setup clock (controls how many frames per second we run)
        self.clock = pygame.time.Clock()
        self.running = True

        # 4. Setup fonts for text and modals
        self.font = pygame.font.SysFont("monospace", 16, bold=True)
        self.modal_font = pygame.font.SysFont("monospace", 20, bold=True)

        # 5. Initialize the first level and the player
        self.current_level_idx = 0
        self.load_level(self.current_level_idx)

    def load_level(self, index: int):
        """Loads a specific level by its index and spawns the player at start."""
        self.current_level_idx = index
        self.level = Level(self.current_level_idx)
        start_x, start_y = self.level.player_start
        self.player = Player(start_x, start_y)

    def handle_events(self):
        """Processes all user inputs (keyboard presses, window close)."""
        for event in pygame.event.get():
            # Player clicked the window 'X' close button
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                # Pressing ESC exits the game
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return

                # If the level was cleared, handle progression
                if self.level.is_won:
                    if event.key == pygame.K_RETURN:
                        self.advance_level()
                    continue

                # Gameplay Controls:
                # 1. Dimension Shifting (Shift keys)
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    self.level.toggle_shift(self.player.grid_x, self.player.grid_y)

                # 2. Movement (Arrow keys or WASD)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.player.move(0, -1, self.level)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.player.move(0, 1, self.level)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.player.move(-1, 0, self.level)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.player.move(1, 0, self.level)

    def advance_level(self):
        """Advances to the next level or loops back to the beginning if all are beaten."""
        if self.current_level_idx + 1 < len(LEVELS):
            self.load_level(self.current_level_idx + 1)
        else:
            # Reached the end! Loop back to Level 1
            self.load_level(0)

    def update(self):
        """Updates game logic: checks if player walked on terminals or the exit."""
        if not self.level.is_won:
            self.level.update(self.player.grid_x, self.player.grid_y)

    def draw_grid_lines(self):
        """Draws subtle grid lines to help visualize tiles."""
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID_LINE, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID_LINE, (0, y), (SCREEN_WIDTH, y))

    def draw_hud(self):
        """Draws the top bar showing level name, dimension, and rebooted servers."""
        rebooted = sum(1 for t in self.level.terminals if t.rebooted)
        total = len(self.level.terminals)
        dim_name = "CORRUPTED" if self.level.is_corrupted else "NORMAL"

        text = f"{self.level.name} | [{dim_name}] | Servers: {rebooted}/{total}"
        hud_surf = self.font.render(text, True, COLOR_TEXT)
        self.screen.blit(hud_surf, (16, 12))

    def draw_level_clear(self):
        """Draws a semi-transparent modal overlay when the level is completed."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        is_final = (self.current_level_idx == len(LEVELS) - 1)
        if is_final:
            header = self.modal_font.render(
                "ALL SERVERS RESTORED! SYSTEM OPERATIONAL!", True, (52, 211, 153)
            )
            sub = self.modal_font.render(
                "Press ENTER to play again or ESC to exit", True, COLOR_TEXT
            )
        else:
            header = self.modal_font.render("SECTOR CLEARED!", True, (52, 211, 153))
            sub = self.modal_font.render(
                "Press ENTER to proceed to the next sub-level", True, COLOR_TEXT
            )

        self.screen.blit(
            header,
            (SCREEN_WIDTH // 2 - header.get_width() // 2, SCREEN_HEIGHT // 2 - 30),
        )
        self.screen.blit(
            sub,
            (SCREEN_WIDTH // 2 - sub.get_width() // 2, SCREEN_HEIGHT // 2 + 15),
        )

    def draw(self):
        """Renders everything to the display."""
        # 1. Draw level tiles (floor and walls)
        self.level.draw(self.screen)

        # 2. Draw grid lines
        self.draw_grid_lines()

        # 3. Draw player
        self.player.draw(self.screen)

        # 4. Draw HUD (top info bar)
        self.draw_hud()

        # 5. Draw modal banner if won
        if self.level.is_won:
            self.draw_level_clear()

        # 6. Flip the display buffer to show changes on screen
        pygame.display.flip()

    def run(self):
        """The main game loop running at 60 FPS."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        # Cleanup when loop ends
        pygame.quit()
        sys.exit()
