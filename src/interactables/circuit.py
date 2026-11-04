import math
import pygame
from src.config import (
    TILE_SIZE,
    COLOR_PLATE_BASE,
    COLOR_PLATE_PRESSED,
    COLOR_PLATE_UNPRESSED,
    COLOR_LASER_CORRUPT,
    COLOR_LASER_NORMAL,
)
from src.interactables.dimension import is_in_dimension


class PressurePlate:
    """
    Floor activation switch. Sends an active signal on its assigned channel
    when weighed down by the player or an active RAM block.
    """
    def __init__(self, grid_x: int, grid_y: int, channel: str = "A", dimension: str = "both"):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.channel = channel
        self.dimension = dimension
        self.is_pressed = False

    def is_active(self, is_corrupted: bool) -> bool:
        return is_in_dimension(self.dimension, is_corrupted)

    def update(self, player_x: int, player_y: int, blocks: list, is_corrupted: bool) -> bool:
        if not self.is_active(is_corrupted):
            prev = self.is_pressed
            self.is_pressed = False
            return prev != self.is_pressed

        occupied = (player_x == self.grid_x and player_y == self.grid_y)
        if not occupied:
            for b in blocks:
                if b.is_active(is_corrupted) and b.grid_x == self.grid_x and b.grid_y == self.grid_y:
                    occupied = True
                    break

        state_changed = (occupied != self.is_pressed)
        self.is_pressed = occupied
        return state_changed

    def draw(self, surface: pygame.Surface, is_corrupted: bool):
        if not self.is_active(is_corrupted):
            return

        pixel_x = self.grid_x * TILE_SIZE
        pixel_y = self.grid_y * TILE_SIZE
        tile_center_x = pixel_x + (TILE_SIZE // 2)
        tile_center_y = pixel_y + (TILE_SIZE // 2)

        padding = 4
        size = TILE_SIZE - (padding * 2)
        rect = pygame.Rect(pixel_x + padding, pixel_y + padding, size, size)

        pygame.draw.rect(surface, COLOR_PLATE_BASE, rect, border_radius=6)
        pygame.draw.rect(surface, (90, 110, 140), rect, width=1, border_radius=6)

        diamond_color = COLOR_PLATE_PRESSED if self.is_pressed else COLOR_PLATE_UNPRESSED
        inner_r = 10 if self.is_pressed else 12

        points = [
            (tile_center_x, tile_center_y - inner_r),
            (tile_center_x + inner_r, tile_center_y),
            (tile_center_x, tile_center_y + inner_r),
            (tile_center_x - inner_r, tile_center_y),
        ]
        pygame.draw.polygon(surface, diamond_color, points)
        pygame.draw.polygon(surface, (255, 255, 255), points, width=1)

        font = pygame.font.SysFont("monospace", 10, bold=True)
        txt = font.render(self.channel, True, (20, 30, 45) if self.is_pressed else (200, 220, 240))
        surface.blit(txt, (tile_center_x - txt.get_width() // 2, tile_center_y - txt.get_height() // 2))


class LaserBarrier:
    """
    High-energy firewall barrier.
    Blocks the player unless powered off by a pressure plate on the same channel
    or shielded by a RAM block.
    """
    def __init__(self, grid_x: int, grid_y: int, channel: str = "A", dimension: str = "corrupt", orientation: str = "horizontal"):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.channel = channel
        self.dimension = dimension
        self.orientation = orientation

    def is_visible(self, is_corrupted: bool) -> bool:
        return is_in_dimension(self.dimension, is_corrupted)

    def is_active(self, is_corrupted: bool, active_channels: set[str]) -> bool:
        if not self.is_visible(is_corrupted):
            return False
        return self.channel not in active_channels

    def draw(self, surface: pygame.Surface, is_corrupted: bool, active_channels: set[str]):
        if not self.is_visible(is_corrupted):
            return

        pixel_x = self.grid_x * TILE_SIZE
        pixel_y = self.grid_y * TILE_SIZE
        tile_center_x = pixel_x + (TILE_SIZE // 2)
        tile_center_y = pixel_y + (TILE_SIZE // 2)

        active = self.is_active(is_corrupted, active_channels)

        if active:
            t = pygame.time.get_ticks() / 1000.0
            beam_pulse = 0.8 + 0.2 * math.sin(t * 12.0)
            laser_color = COLOR_LASER_CORRUPT if is_corrupted else COLOR_LASER_NORMAL

            if self.orientation == "horizontal":
                pygame.draw.rect(surface, (80, 80, 95), (pixel_x, tile_center_y - 6, 6, 12), border_radius=2)
                pygame.draw.rect(surface, (80, 80, 95), (pixel_x + TILE_SIZE - 6, tile_center_y - 6, 6, 12), border_radius=2)

                glow_h = int(8 * beam_pulse)
                glow_surf = pygame.Surface((TILE_SIZE, glow_h), pygame.SRCALPHA)
                glow_surf.fill((*laser_color, 120))
                surface.blit(glow_surf, (pixel_x, tile_center_y - glow_h // 2))

                pygame.draw.line(surface, (255, 255, 255), (pixel_x + 4, tile_center_y), (pixel_x + TILE_SIZE - 4, tile_center_y), width=2)
            else:
                pygame.draw.rect(surface, (80, 80, 95), (tile_center_x - 6, pixel_y, 12, 6), border_radius=2)
                pygame.draw.rect(surface, (80, 80, 95), (tile_center_x - 6, pixel_y + TILE_SIZE - 6, 12, 6), border_radius=2)

                glow_w = int(8 * beam_pulse)
                glow_surf = pygame.Surface((glow_w, TILE_SIZE), pygame.SRCALPHA)
                glow_surf.fill((*laser_color, 120))
                surface.blit(glow_surf, (tile_center_x - glow_w // 2, pixel_y))

                pygame.draw.line(surface, (255, 255, 255), (tile_center_x, pixel_y + 4), (tile_center_x, pixel_y + TILE_SIZE - 4), width=2)
        else:
            if self.orientation == "horizontal":
                pygame.draw.rect(surface, (50, 60, 75), (pixel_x, tile_center_y - 5, 4, 10), border_radius=2)
                pygame.draw.rect(surface, (50, 60, 75), (pixel_x + TILE_SIZE - 4, tile_center_y - 5, 4, 10), border_radius=2)
                pygame.draw.line(surface, (50, 70, 95), (pixel_x + 6, tile_center_y), (pixel_x + TILE_SIZE - 6, tile_center_y), width=1)
            else:
                pygame.draw.rect(surface, (50, 60, 75), (tile_center_x - 5, pixel_y, 10, 4), border_radius=2)
                pygame.draw.rect(surface, (50, 60, 75), (tile_center_x - 5, pixel_y + TILE_SIZE - 4, 10, 4), border_radius=2)
                pygame.draw.line(surface, (50, 70, 95), (tile_center_x, pixel_y + 6), (tile_center_x, pixel_y + TILE_SIZE - 6), width=1)
