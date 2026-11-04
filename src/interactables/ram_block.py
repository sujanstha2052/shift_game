import pygame
from src.config import (
    TILE_SIZE,
    COLOR_RAM_QUANTUM_BG,
    COLOR_RAM_QUANTUM_BORDER,
    COLOR_RAM_NORMAL_BG,
    COLOR_RAM_NORMAL_BORDER,
    COLOR_RAM_CORRUPT_BG,
    COLOR_RAM_CORRUPT_BORDER,
)
from src.interactables.dimension import is_in_dimension


class RAMBlock:
    """
    Sokoban-style pushable memory crate.
    Can exist in 'normal', 'corrupt', or 'both' dimensions.
    """
    def __init__(self, grid_x: int, grid_y: int, dimension: str = "both"):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.dimension = dimension

        self.pixel_x = float(grid_x * TILE_SIZE)
        self.pixel_y = float(grid_y * TILE_SIZE)
        self.lerp_speed = 0.35

    @property
    def target_pixel_x(self) -> float:
        return float(self.grid_x * TILE_SIZE)

    @property
    def target_pixel_y(self) -> float:
        return float(self.grid_y * TILE_SIZE)

    def is_active(self, is_corrupted: bool) -> bool:
        return is_in_dimension(self.dimension, is_corrupted)

    def reset_position(self, grid_x: int, grid_y: int):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x = float(grid_x * TILE_SIZE)
        self.pixel_y = float(grid_y * TILE_SIZE)

    def push(self, dx: int, dy: int):
        self.grid_x += dx
        self.grid_y += dy

    def update(self):
        diff_x = self.target_pixel_x - self.pixel_x
        diff_y = self.target_pixel_y - self.pixel_y

        if abs(diff_x) < 0.5:
            self.pixel_x = self.target_pixel_x
        else:
            self.pixel_x += diff_x * self.lerp_speed

        if abs(diff_y) < 0.5:
            self.pixel_y = self.target_pixel_y
        else:
            self.pixel_y += diff_y * self.lerp_speed

    def draw(self, surface: pygame.Surface, is_corrupted: bool):
        if not self.is_active(is_corrupted):
            return

        padding = 4
        size = TILE_SIZE - (padding * 2)
        rx = int(self.pixel_x) + padding
        ry = int(self.pixel_y) + padding
        rect = pygame.Rect(rx, ry, size, size)

        # Dimension-specific palette
        if self.dimension == "both":
            bg_color = COLOR_RAM_QUANTUM_BG
            border_color = COLOR_RAM_QUANTUM_BORDER
            symbol_color = (255, 230, 130)
        elif self.dimension == "corrupt":
            bg_color = COLOR_RAM_CORRUPT_BG
            border_color = COLOR_RAM_CORRUPT_BORDER
            symbol_color = (255, 150, 180)
        else:
            bg_color = COLOR_RAM_NORMAL_BG
            border_color = COLOR_RAM_NORMAL_BORDER
            symbol_color = (160, 215, 255)

        pygame.draw.rect(surface, bg_color, rect, border_radius=5)
        pygame.draw.rect(surface, border_color, rect, width=2, border_radius=5)

        center_x = rx + size // 2
        center_y = ry + size // 2
        inner_chip = pygame.Rect(center_x - 6, center_y - 6, 12, 12)
        pygame.draw.rect(surface, symbol_color, inner_chip, border_radius=2)

        rivet_color = (255, 255, 255)
        for ox, oy in [(-size//2 + 4, -size//2 + 4), (size//2 - 4, -size//2 + 4),
                       (-size//2 + 4, size//2 - 4), (size//2 - 4, size//2 - 4)]:
            pygame.draw.circle(surface, rivet_color, (center_x + ox, center_y + oy), 1)
