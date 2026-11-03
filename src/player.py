import pygame
from src.config import TILE_SIZE, COLOR_PLAYER, COLOR_PLAYER_BORDER


class Player:
    """
    Represents the player avatar.
    Features:
    - Logical grid coordinates (grid_x, grid_y)
    - Smooth interpolated pixel movement (pixel_x, pixel_y)
    - Directional facing (facing_x, facing_y) with a glowing cyber-visor
    - Squash and stretch animation on movement
    """

    def __init__(self, grid_x: int, grid_y: int):
        # 1. Logical Grid Coordinates (integers)
        self.grid_x = grid_x
        self.grid_y = grid_y

        # 2. Visual Pixel Coordinates (floats for smooth sliding)
        self.pixel_x = float(grid_x * TILE_SIZE)
        self.pixel_y = float(grid_y * TILE_SIZE)
        self.lerp_speed = 0.35

        # 3. Directional Facing (default facing right: dx=1, dy=0)
        self.facing_x = 1
        self.facing_y = 0

        # 4. Squash & Stretch Scale (1.0 = normal size)
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.spring_speed = 0.20  # How fast it bounces back to 1.0

    @property
    def target_pixel_x(self) -> float:
        return float(self.grid_x * TILE_SIZE)

    @property
    def target_pixel_y(self) -> float:
        return float(self.grid_y * TILE_SIZE)

    @property
    def is_moving(self) -> bool:
        return (
            abs(self.pixel_x - self.target_pixel_x) > 0.5
            or abs(self.pixel_y - self.target_pixel_y) > 0.5
        )

    def reset_position(self, grid_x: int, grid_y: int):
        """Instantly relocates the player to a spawn tile."""
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x = float(grid_x * TILE_SIZE)
        self.pixel_y = float(grid_y * TILE_SIZE)
        self.scale_x = 1.0
        self.scale_y = 1.0

    def move(self, dx: int, dy: int, level) -> bool:
        """
        Attempts to move by (dx, dy).
        If valid, triggers movement and squash & stretch!
        """
        if self.is_moving:
            return False

        # Always update facing direction when an input is given
        self.facing_x = dx
        self.facing_y = dy

        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        if not level.is_solid(new_x, new_y):
            # Valid move: update grid and stretch in direction of motion
            self.grid_x = new_x
            self.grid_y = new_y

            if dx != 0:
                self.scale_x = 1.25  # Wider
                self.scale_y = 0.80  # Flatter
            elif dy != 0:
                self.scale_x = 0.80  # Thinner
                self.scale_y = 1.25  # Taller

            return True

        # --- Wall Bump Feedback ---
        # When hitting a solid wall:
        # 1. Nudge visual position 7px toward the wall
        self.pixel_x += dx * 7.0
        self.pixel_y += dy * 7.0

        # 2. Compress against the wall surface
        if dx != 0:
            self.scale_x = 0.82
            self.scale_y = 1.18
        elif dy != 0:
            self.scale_x = 1.18
            self.scale_y = 0.82

        return False

    def update(self):
        """
        Runs every frame (60 FPS):
        1. Slides pixel position toward target tile (position lerp).
        2. Recovers squash & stretch back to 1.0 (spring recovery).
        """
        # --- 1. Movement Lerp ---
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

        # --- 2. Squash & Stretch Recovery ---
        # Smoothly pull scale_x and scale_y back towards 1.0
        self.scale_x += (1.0 - self.scale_x) * self.spring_speed
        self.scale_y += (1.0 - self.scale_y) * self.spring_speed

    def draw(self, surface: pygame.Surface):
        """
        Draws the animated character with centered scaling and a directional visor.
        """
        padding = 6
        base_size = TILE_SIZE - (padding * 2)  # Normal size ~36px

        # Compute dynamic stretched width & height
        width = base_size * self.scale_x
        height = base_size * self.scale_y

        # Center the stretched rectangle inside the tile
        tile_center_x = self.pixel_x + (TILE_SIZE / 2)
        tile_center_y = self.pixel_y + (TILE_SIZE / 2)

        body_rect = pygame.Rect(
            int(tile_center_x - (width / 2)),
            int(tile_center_y - (height / 2)),
            int(width),
            int(height),
        )

        # 1. Draw Player Body
        pygame.draw.rect(surface, COLOR_PLAYER, body_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_PLAYER_BORDER, body_rect, width=2, border_radius=6)

        # 2. Draw Directional Visor / Eyes
        # Offset the visor based on facing direction
        visor_w = 8 if self.facing_x != 0 else 16
        visor_h = 16 if self.facing_x != 0 else 8

        offset_x = self.facing_x * 8
        offset_y = self.facing_y * 8

        visor_rect = pygame.Rect(
            int(tile_center_x - (visor_w / 2) + offset_x),
            int(tile_center_y - (visor_h / 2) + offset_y),
            visor_w,
            visor_h,
        )

        # Bright neon visor with a dark outline
        pygame.draw.rect(surface, (255, 255, 255), visor_rect, border_radius=2)
        pygame.draw.rect(surface, (20, 40, 70), visor_rect, width=1, border_radius=2)
