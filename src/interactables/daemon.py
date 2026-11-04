import math
import pygame
from src.config import (
    TILE_SIZE,
    COLOR_DAEMON_ACTIVE,
    COLOR_DAEMON_BORDER,
    COLOR_DAEMON_DORMANT,
)


class DaemonSentinel:
    """
    Hostile corrupted system process that patrols fixed waypoint routes.
    Freezes dormantly in the Normal dimension, but steps each turn in the Corrupted dimension.
    """
    def __init__(self, patrol_points: list[tuple[int, int]], loop: bool = False):
        self.patrol_points = patrol_points
        self.loop = loop
        self.point_index = 0
        self.direction = 1

        start_x, start_y = patrol_points[0]
        self.grid_x = start_x
        self.grid_y = start_y

        self.pixel_x = float(start_x * TILE_SIZE)
        self.pixel_y = float(start_y * TILE_SIZE)
        self.lerp_speed = 0.35

    @property
    def target_pixel_x(self) -> float:
        return float(self.grid_x * TILE_SIZE)

    @property
    def target_pixel_y(self) -> float:
        return float(self.grid_y * TILE_SIZE)

    def reset_state(self, grid_x: int, grid_y: int, point_index: int, direction: int):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.point_index = point_index
        self.direction = direction
        self.pixel_x = float(grid_x * TILE_SIZE)
        self.pixel_y = float(grid_y * TILE_SIZE)

    def step_patrol(self):
        if len(self.patrol_points) <= 1:
            return

        if self.loop:
            self.point_index = (self.point_index + 1) % len(self.patrol_points)
        else:
            next_idx = self.point_index + self.direction
            if next_idx >= len(self.patrol_points) or next_idx < 0:
                self.direction *= -1
                next_idx = self.point_index + self.direction
            self.point_index = next_idx

        self.grid_x, self.grid_y = self.patrol_points[self.point_index]

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
        padding = 5
        size = TILE_SIZE - (padding * 2)
        rx = int(self.pixel_x) + padding
        ry = int(self.pixel_y) + padding
        tile_center_x = rx + size // 2
        tile_center_y = ry + size // 2
        body_rect = pygame.Rect(rx, ry, size, size)

        t = pygame.time.get_ticks() / 1000.0

        if is_corrupted:
            pulse = (math.sin(t * 7.0) + 1.0) / 2.0

            halo_size = int(size + 6 + (4 * pulse))
            halo_surf = pygame.Surface((halo_size, halo_size), pygame.SRCALPHA)
            halo_surf.fill((*COLOR_DAEMON_BORDER, int(50 + 40 * pulse)))
            surface.blit(halo_surf, (tile_center_x - halo_size // 2, tile_center_y - halo_size // 2))

            pygame.draw.rect(surface, COLOR_DAEMON_ACTIVE, body_rect, border_radius=8)
            pygame.draw.rect(surface, COLOR_DAEMON_BORDER, body_rect, width=2, border_radius=8)

            eye_r = int(5 + (2 * pulse))
            pygame.draw.circle(surface, (255, 240, 90), (tile_center_x, tile_center_y), eye_r)
            pygame.draw.circle(surface, (255, 255, 255), (tile_center_x, tile_center_y), 2)
        else:
            pygame.draw.rect(surface, COLOR_DAEMON_DORMANT, body_rect, border_radius=8)
            pygame.draw.rect(surface, (60, 75, 95), body_rect, width=1, border_radius=8)
            pygame.draw.circle(surface, (70, 85, 105), (tile_center_x, tile_center_y), 3)
