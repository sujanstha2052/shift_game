import pygame
from src.config import (
    TILE_SIZE,
    COLOR_TERMINAL_OFF,
    COLOR_TERMINAL_REBOOTED,
    COLOR_EXIT_LOCKED,
    COLOR_EXIT_OPEN,
)

class Terminal:
    def __init__(self, grid_x: int, grid_y: int, required_in_corrupt: bool = False):
        self.grid_x = grid_x
        self.grid_y = grid_y
        # If True, this server exists in the corrupted dimension; otherwise in normal
        self.exists_in_corrupt = required_in_corrupt
        self.rebooted = False

    def is_visible(self, is_corrupted_dimension: bool) -> bool:
        """A terminal only exists in its assigned dimension."""
        return self.exists_in_corrupt == is_corrupted_dimension

    def check_interaction(self, player_x: int, player_y: int, is_corrupted: bool) -> bool:
        """Returns True if the player steps onto this terminal in the matching dimension."""
        if not self.rebooted and self.is_visible(is_corrupted):
            if self.grid_x == player_x and self.grid_y == player_y:
                self.rebooted = True
                return True
        return False

    def draw(self, surface: pygame.Surface, is_corrupted: bool):
        if not self.is_visible(is_corrupted):
            return

        pixel_x = self.grid_x * TILE_SIZE
        pixel_y = self.grid_y * TILE_SIZE
        padding = 10
        inner_size = TILE_SIZE - (padding * 2)

        rect = pygame.Rect(pixel_x + padding, pixel_y + padding, inner_size, inner_size)
        color = COLOR_TERMINAL_REBOOTED if self.rebooted else COLOR_TERMINAL_OFF
        
        # Draw server terminal core
        pygame.draw.rect(surface, color, rect, border_radius=4)
        # Indicator border
        pygame.draw.rect(surface, (255, 255, 255), rect, width=1, border_radius=4)


class ExitDoor:
    def __init__(self, grid_x: int, grid_y: int):
        self.grid_x = grid_x
        self.grid_y = grid_y

    def draw(self, surface: pygame.Surface, is_open: bool):
        pixel_x = self.grid_x * TILE_SIZE
        pixel_y = self.grid_y * TILE_SIZE
        padding = 6
        inner_size = TILE_SIZE - (padding * 2)

        rect = pygame.Rect(pixel_x + padding, pixel_y + padding, inner_size, inner_size)
        color = COLOR_EXIT_OPEN if is_open else COLOR_EXIT_LOCKED

        pygame.draw.rect(surface, color, rect, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255), rect, width=2, border_radius=8)

    def is_entered(self, player_x: int, player_y: int, is_open: bool) -> bool:
        return is_open and (self.grid_x == player_x and self.grid_y == player_y)