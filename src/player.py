import pygame
from src.config import TILE_SIZE, COLOR_PLAYER, COLOR_PLAYER_BORDER

class Player:
    def __init__(self, grid_x: int, grid_y: int):
        self.grid_x = grid_x
        self.grid_y = grid_y

    def reset_position(self, grid_x: int, grid_y: int):
        """Relocates the player to a designated spawn tile."""
        self.grid_x = grid_x
        self.grid_y = grid_y

    def move(self, dx: int, dy: int, level):
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        if not level.is_solid(new_x, new_y):
            self.grid_x = new_x
            self.grid_y = new_y

    def draw(self, surface: pygame.Surface):
        pixel_x = self.grid_x * TILE_SIZE
        pixel_y = self.grid_y * TILE_SIZE
        padding = 6
        inner_size = TILE_SIZE - (padding * 2)

        rect = pygame.Rect(
            pixel_x + padding,
            pixel_y + padding,
            inner_size,
            inner_size,
        )

        pygame.draw.rect(surface, COLOR_PLAYER, rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_PLAYER_BORDER, rect, width=2, border_radius=6)