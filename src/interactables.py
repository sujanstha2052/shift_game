import math
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
        tile_center_x = pixel_x + (TILE_SIZE // 2)
        tile_center_y = pixel_y + (TILE_SIZE // 2)

        # Pulse animation factor (0.0 to 1.0) using sine of game clock
        t = pygame.time.get_ticks() / 1000.0
        pulse = (math.sin(t * 3.5) + 1.0) / 2.0

        base_color = COLOR_TERMINAL_REBOOTED if self.rebooted else COLOR_TERMINAL_OFF

        # --- 1. Ambient Pulsing Halo ---
        halo_alpha = int(35 + (50 * pulse)) if not self.rebooted else 40
        halo_expand = int(3 * pulse) if not self.rebooted else 1
        halo_size = (TILE_SIZE - 10) + (halo_expand * 2)

        halo_surf = pygame.Surface((halo_size, halo_size), pygame.SRCALPHA)
        halo_surf.fill((*base_color, halo_alpha))
        surface.blit(
            halo_surf,
            (tile_center_x - halo_size // 2, tile_center_y - halo_size // 2),
        )

        # --- 2. Server Terminal Body ---
        padding = 9
        inner_size = TILE_SIZE - (padding * 2)
        rect = pygame.Rect(pixel_x + padding, pixel_y + padding, inner_size, inner_size)
        pygame.draw.rect(surface, base_color, rect, border_radius=4)
        pygame.draw.rect(surface, (255, 255, 255), rect, width=1, border_radius=4)

        # --- 3. Hardware Status Indicator LEDs ---
        led_spacing = 6
        led_start_x = tile_center_x - led_spacing
        led_y = pixel_y + padding + 6

        for i in range(3):
            lx = led_start_x + (i * led_spacing)
            if self.rebooted:
                # All 3 LEDs solid glowing green
                led_color = (200, 255, 220)
            else:
                # In offline mode, LEDs blink
                blink_on = ((int(t * 5.0) + i) % 2 == 0)
                led_color = (255, 220, 150) if blink_on else (120, 70, 10)
            pygame.draw.circle(surface, led_color, (lx, led_y), 2)


class ExitDoor:
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
            # Active Portal: Pulsing radiant green gateway aura
            halo_size = int(TILE_SIZE - 4 + (4 * pulse))
            halo_alpha = int(50 + (60 * pulse))
            halo_surf = pygame.Surface((halo_size, halo_size), pygame.SRCALPHA)
            halo_surf.fill((*COLOR_EXIT_OPEN, halo_alpha))
            surface.blit(
                halo_surf,
                (tile_center_x - halo_size // 2, tile_center_y - halo_size // 2),
            )

        padding = 6
        inner_size = TILE_SIZE - (padding * 2)
        rect = pygame.Rect(pixel_x + padding, pixel_y + padding, inner_size, inner_size)
        color = COLOR_EXIT_OPEN if is_open else COLOR_EXIT_LOCKED

        pygame.draw.rect(surface, color, rect, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255), rect, width=2, border_radius=8)

        # Center indicator icon (Glowing portal ring if open, lock dot if closed)
        if is_open:
            pygame.draw.circle(
                surface,
                (255, 255, 255),
                (tile_center_x, tile_center_y),
                int(5 + pulse * 2),
                width=2,
            )
        else:
            pygame.draw.circle(surface, (255, 200, 200), (tile_center_x, tile_center_y), 3)

    def is_entered(self, player_x: int, player_y: int, is_open: bool) -> bool:
        return is_open and (self.grid_x == player_x and self.grid_y == player_y)


# =============================================================================
# 3. RAM BLOCK (Pushable Memory Crate)
# =============================================================================
class RAMBlock:
    """
    A pushable memory crate.
    Can exist in 'normal', 'corrupt', or 'both' dimensions.
    Features smooth lerping movement when pushed.
    """
    def __init__(self, grid_x: int, grid_y: int, dimension: str = "both"):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.dimension = dimension  # "normal", "corrupt", or "both"

        # Visual smooth interpolation
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
        """Returns True if the block is physical in the current dimension."""
        if self.dimension == "both":
            return True
        elif self.dimension == "corrupt":
            return is_corrupted
        elif self.dimension == "normal":
            return not is_corrupted
        return False

    def reset_position(self, grid_x: int, grid_y: int):
        """Used by the undo system or level restart."""
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x = float(grid_x * TILE_SIZE)
        self.pixel_y = float(grid_y * TILE_SIZE)

    def push(self, dx: int, dy: int):
        """Pushes the block by (dx, dy)."""
        self.grid_x += dx
        self.grid_y += dy

    def update(self):
        """Smoothly lerps visual position toward target grid coordinates."""
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

        # Style by dimension type
        if self.dimension == "both":
            # Quantum Shared Memory: Deep indigo with gold circuits
            bg_color = (75, 45, 115)
            border_color = (245, 195, 65)
            symbol_color = (255, 230, 130)
        elif self.dimension == "corrupt":
            # Corrupted Memory: Crimson with neon pink edge
            bg_color = (120, 25, 45)
            border_color = (255, 65, 115)
            symbol_color = (255, 150, 180)
        else:
            # Normal Memory: Heavy steel blue with cyan traces
            bg_color = (45, 65, 90)
            border_color = (65, 160, 240)
            symbol_color = (160, 215, 255)

        # Draw outer block body
        pygame.draw.rect(surface, bg_color, rect, border_radius=5)
        pygame.draw.rect(surface, border_color, rect, width=2, border_radius=5)

        # Draw RAM chip micro-circuit center pattern
        center_x = rx + size // 2
        center_y = ry + size // 2
        inner_chip = pygame.Rect(center_x - 6, center_y - 6, 12, 12)
        pygame.draw.rect(surface, symbol_color, inner_chip, border_radius=2)

        # Cross corner rivets
        rivet_color = (255, 255, 255)
        for ox, oy in [(-size//2 + 4, -size//2 + 4), (size//2 - 4, -size//2 + 4),
                       (-size//2 + 4, size//2 - 4), (size//2 - 4, size//2 - 4)]:
            pygame.draw.circle(surface, rivet_color, (center_x + ox, center_y + oy), 1)


# =============================================================================
# 4. DATA PRESSURE PLATE (Floor Activation Pad)
# =============================================================================
class PressurePlate:
    """
    A floor circuit pad.
    Weighed down when either the player OR a RAM block is on its coordinates.
    Emits an active signal on its assigned channel (e.g. 'A').
    """
    def __init__(self, grid_x: int, grid_y: int, channel: str = "A", dimension: str = "both"):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.channel = channel
        self.dimension = dimension  # "normal", "corrupt", or "both"
        self.is_pressed = False

    def is_active(self, is_corrupted: bool) -> bool:
        if self.dimension == "both":
            return True
        elif self.dimension == "corrupt":
            return is_corrupted
        elif self.dimension == "normal":
            return not is_corrupted
        return False

    def update(self, player_x: int, player_y: int, blocks: list, is_corrupted: bool) -> bool:
        """
        Updates whether player or a block is standing on the plate.
        Returns True if the state changed this frame (triggering a click sound).
        """
        if not self.is_active(is_corrupted):
            prev = self.is_pressed
            self.is_pressed = False
            return prev != self.is_pressed

        # Check if player is on plate
        occupied = (player_x == self.grid_x and player_y == self.grid_y)

        # Check if any active RAM block is on plate
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

        # Draw outer metal base frame
        padding = 4
        size = TILE_SIZE - (padding * 2)
        rect = pygame.Rect(pixel_x + padding, pixel_y + padding, size, size)

        base_color = (40, 50, 70) if not is_corrupted else (60, 25, 40)
        pygame.draw.rect(surface, base_color, rect, border_radius=6)
        pygame.draw.rect(surface, (90, 110, 140), rect, width=1, border_radius=6)

        # Inner pressure diamond contact pad
        diamond_color = (52, 211, 153) if self.is_pressed else (120, 140, 170)
        inner_r = 10 if self.is_pressed else 12

        points = [
            (tile_center_x, tile_center_y - inner_r),
            (tile_center_x + inner_r, tile_center_y),
            (tile_center_x, tile_center_y + inner_r),
            (tile_center_x - inner_r, tile_center_y),
        ]
        pygame.draw.polygon(surface, diamond_color, points)
        pygame.draw.polygon(surface, (255, 255, 255), points, width=1)

        # Channel text indicator
        font = pygame.font.SysFont("monospace", 10, bold=True)
        txt = font.render(self.channel, True, (20, 30, 45) if self.is_pressed else (200, 220, 240))
        surface.blit(txt, (tile_center_x - txt.get_width() // 2, tile_center_y - txt.get_height() // 2))


# =============================================================================
# 5. FIREWALL / LASER BARRIER
# =============================================================================
class LaserBarrier:
    """
    High-energy laser conduit barrier.
    Deactivates when its linked pressure plate channel is pressed.
    Blocks player movement when active.
    """
    def __init__(self, grid_x: int, grid_y: int, channel: str = "A", dimension: str = "corrupt", orientation: str = "horizontal"):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.channel = channel
        self.dimension = dimension  # "normal", "corrupt", or "both"
        self.orientation = orientation  # "horizontal" or "vertical"

    def is_visible(self, is_corrupted: bool) -> bool:
        if self.dimension == "both":
            return True
        elif self.dimension == "corrupt":
            return is_corrupted
        elif self.dimension == "normal":
            return not is_corrupted
        return False

    def is_active(self, is_corrupted: bool, active_channels: set[str]) -> bool:
        """Laser is energized if visible in this dimension AND its channel is NOT pressed."""
        if not self.is_visible(is_corrupted):
            return False
        # If the channel is pressed by a plate, laser turns OFF
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
            # Active Laser: pulsating glowing beam
            t = pygame.time.get_ticks() / 1000.0
            beam_pulse = 0.8 + 0.2 * math.sin(t * 12.0)
            laser_color = (255, 45, 85) if is_corrupted else (45, 175, 255)

            if self.orientation == "horizontal":
                # Emitter nodes at left and right
                pygame.draw.rect(surface, (80, 80, 95), (pixel_x, tile_center_y - 6, 6, 12), border_radius=2)
                pygame.draw.rect(surface, (80, 80, 95), (pixel_x + TILE_SIZE - 6, tile_center_y - 6, 6, 12), border_radius=2)

                # Outer glow beam
                glow_h = int(8 * beam_pulse)
                glow_surf = pygame.Surface((TILE_SIZE, glow_h), pygame.SRCALPHA)
                glow_surf.fill((*laser_color, 120))
                surface.blit(glow_surf, (pixel_x, tile_center_y - glow_h // 2))

                # Core white hot laser line
                pygame.draw.line(surface, (255, 255, 255), (pixel_x + 4, tile_center_y), (pixel_x + TILE_SIZE - 4, tile_center_y), width=2)
            else:
                # Vertical beam
                pygame.draw.rect(surface, (80, 80, 95), (tile_center_x - 6, pixel_y, 12, 6), border_radius=2)
                pygame.draw.rect(surface, (80, 80, 95), (tile_center_x - 6, pixel_y + TILE_SIZE - 6, 12, 6), border_radius=2)

                glow_w = int(8 * beam_pulse)
                glow_surf = pygame.Surface((glow_w, TILE_SIZE), pygame.SRCALPHA)
                glow_surf.fill((*laser_color, 120))
                surface.blit(glow_surf, (tile_center_x - glow_w // 2, pixel_y))

                pygame.draw.line(surface, (255, 255, 255), (tile_center_x, pixel_y + 4), (tile_center_x, pixel_y + TILE_SIZE - 4), width=2)
        else:
            # Deactivated / Safe conduit: dim emitters and safe dashed line
            if self.orientation == "horizontal":
                pygame.draw.rect(surface, (50, 60, 75), (pixel_x, tile_center_y - 5, 4, 10), border_radius=2)
                pygame.draw.rect(surface, (50, 60, 75), (pixel_x + TILE_SIZE - 4, tile_center_y - 5, 4, 10), border_radius=2)
                # Dim safe line
                pygame.draw.line(surface, (50, 70, 95), (pixel_x + 6, tile_center_y), (pixel_x + TILE_SIZE - 6, tile_center_y), width=1)
            else:
                pygame.draw.rect(surface, (50, 60, 75), (tile_center_x - 5, pixel_y, 10, 4), border_radius=2)
                pygame.draw.rect(surface, (50, 60, 75), (tile_center_x - 5, pixel_y + TILE_SIZE - 4, 10, 4), border_radius=2)
                pygame.draw.line(surface, (50, 70, 95), (tile_center_x, pixel_y + 6), (tile_center_x, pixel_y + TILE_SIZE - 6), width=1)


# =============================================================================
# 6. CORRUPTED DAEMON / SENTINEL
# =============================================================================
class DaemonSentinel:
    """
    An automated security daemon patrolling a designated set of waypoints.
    - Dormant and harmless in the Normal Dimension.
    - Active and hostile in the Corrupted Dimension (takes 1 step per player action).
    """
    def __init__(self, patrol_points: list[tuple[int, int]], loop: bool = False):
        self.patrol_points = patrol_points
        self.loop = loop
        self.point_index = 0
        self.direction = 1  # 1 = forward along waypoints, -1 = reverse

        start_x, start_y = patrol_points[0]
        self.grid_x = start_x
        self.grid_y = start_y

        # Visual smooth lerp
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
        """Restores state from the undo history stack."""
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.point_index = point_index
        self.direction = direction
        self.pixel_x = float(grid_x * TILE_SIZE)
        self.pixel_y = float(grid_y * TILE_SIZE)

    def step_patrol(self):
        """Advances one step along the patrol waypoint path."""
        if len(self.patrol_points) <= 1:
            return

        if self.loop:
            self.point_index = (self.point_index + 1) % len(self.patrol_points)
        else:
            next_idx = self.point_index + self.direction
            if next_idx >= len(self.patrol_points) or next_idx < 0:
                self.direction *= -1  # Ping-pong reverse direction
                next_idx = self.point_index + self.direction
            self.point_index = next_idx

        self.grid_x, self.grid_y = self.patrol_points[self.point_index]

    def update(self):
        """Smooth visual interpolation toward target tile."""
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
            # --- ACTIVE CORRUPTED DAEMON ---
            pulse = (math.sin(t * 7.0) + 1.0) / 2.0
            base_color = (165, 20, 55)
            border_color = (255, 60, 110)

            # Red alert halo
            halo_size = int(size + 6 + (4 * pulse))
            halo_surf = pygame.Surface((halo_size, halo_size), pygame.SRCALPHA)
            halo_surf.fill((255, 30, 80, int(50 + 40 * pulse)))
            surface.blit(halo_surf, (tile_center_x - halo_size // 2, tile_center_y - halo_size // 2))

            # Diamond chassis
            pygame.draw.rect(surface, base_color, body_rect, border_radius=8)
            pygame.draw.rect(surface, border_color, body_rect, width=2, border_radius=8)

            # Glowing cyclops scanner eye
            eye_r = int(5 + (2 * pulse))
            pygame.draw.circle(surface, (255, 240, 90), (tile_center_x, tile_center_y), eye_r)
            pygame.draw.circle(surface, (255, 255, 255), (tile_center_x, tile_center_y), 2)
        else:
            # --- DORMANT SHUTDOWN NODE ---
            base_color = (35, 45, 60)
            border_color = (60, 75, 95)

            pygame.draw.rect(surface, base_color, body_rect, border_radius=8)
            pygame.draw.rect(surface, border_color, body_rect, width=1, border_radius=8)

            # Inactive gray sensor dot
            pygame.draw.circle(surface, (70, 85, 105), (tile_center_x, tile_center_y), 3)
