import math
import pygame
from src.config import (
    TILE_SIZE,
    COLOR_TERMINAL_OFF,
    COLOR_TERMINAL_REBOOTED,
)
from src.interactables.dimension import is_in_dimension


class Terminal:
    """
    Server terminal node that the player must reboot.
    Exists in either Normal or Corrupted dimension.
    """
    def __init__(self, grid_x: int, grid_y: int, required_in_corrupt: bool = False):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.dimension = "corrupt" if required_in_corrupt else "normal"
        self.rebooted = False

    def is_visible(self, is_corrupted: bool) -> bool:
        return is_in_dimension(self.dimension, is_corrupted)

    def check_interaction(self, player_x: int, player_y: int, is_corrupted: bool) -> bool:
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
        tile_center_x = pixel_x + (TILE_SIZE // 2)
        tile_center_y = pixel_y + (TILE_SIZE // 2)

        t = pygame.time.get_ticks() / 1000.0
        pulse = (math.sin(t * 3.5) + 1.0) / 2.0
        base_color = COLOR_TERMINAL_REBOOTED if self.rebooted else COLOR_TERMINAL_OFF

        # 1. Ambient Halo
        halo_alpha = int(35 + (50 * pulse)) if not self.rebooted else 40
        halo_expand = int(3 * pulse) if not self.rebooted else 1
        halo_size = (TILE_SIZE - 10) + (halo_expand * 2)

        halo_surf = pygame.Surface((halo_size, halo_size), pygame.SRCALPHA)
        halo_surf.fill((*base_color, halo_alpha))
        surface.blit(halo_surf, (tile_center_x - halo_size // 2, tile_center_y - halo_size // 2))

        # 2. Server Body
        padding = 9
        inner_size = TILE_SIZE - (padding * 2)
        rect = pygame.Rect(pixel_x + padding, pixel_y + padding, inner_size, inner_size)
        pygame.draw.rect(surface, base_color, rect, border_radius=4)
        pygame.draw.rect(surface, (255, 255, 255), rect, width=1, border_radius=4)

        # 3. Status LEDs
        led_spacing = 6
        led_start_x = tile_center_x - led_spacing
        led_y = pixel_y + padding + 6

        for i in range(3):
            lx = led_start_x + (i * led_spacing)
            if self.rebooted:
                led_color = (200, 255, 220)
            else:
                blink_on = ((int(t * 5.0) + i) % 2 == 0)
                led_color = (255, 220, 150) if blink_on else (120, 70, 10)
            pygame.draw.circle(surface, led_color, (lx, led_y), 2)
