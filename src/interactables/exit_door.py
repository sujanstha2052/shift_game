import math
import pygame
from src.config import (
    TILE_SIZE,
    COLOR_EXIT_LOCKED,
    COLOR_EXIT_OPEN,
)


class ExitDoor:
    """
    Exit gateway: opens once all terminals in the level are rebooted.
    """
    def __init__(self, grid_x: int, grid_y: int):
        self.grid_x = grid_x
        self.grid_y = grid_y

    def draw(self, surface: pygame.Surface, is_open: bool):
        pixel_x = self.grid_x * TILE_SIZE
        pixel_y = self.grid_y * TILE_SIZE
        tile_center_x = pixel_x + (TILE_SIZE // 2)
        tile_center_y = pixel_y + (TILE_SIZE // 2)

        t = pygame.time.get_ticks() / 1000.0
        pulse = (math.sin(t * 4.0) + 1.0) / 2.0

        if is_open:
            halo_size = int(TILE_SIZE - 4 + (4 * pulse))
            halo_alpha = int(50 + (60 * pulse))
            halo_surf = pygame.Surface((halo_size, halo_size), pygame.SRCALPHA)
            halo_surf.fill((*COLOR_EXIT_OPEN, halo_alpha))
            surface.blit(halo_surf, (tile_center_x - halo_size // 2, tile_center_y - halo_size // 2))

        padding = 6
        inner_size = TILE_SIZE - (padding * 2)
        rect = pygame.Rect(pixel_x + padding, pixel_y + padding, inner_size, inner_size)
        color = COLOR_EXIT_OPEN if is_open else COLOR_EXIT_LOCKED

        pygame.draw.rect(surface, color, rect, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255), rect, width=2, border_radius=8)

        if is_open:
            pygame.draw.circle(surface, (255, 255, 255), (tile_center_x, tile_center_y), int(5 + pulse * 2), width=2)
        else:
            pygame.draw.circle(surface, (255, 200, 200), (tile_center_x, tile_center_y), 3)

    def is_entered(self, player_x: int, player_y: int, is_open: bool) -> bool:
        return is_open and (self.grid_x == player_x and self.grid_y == player_y)
