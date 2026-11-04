import math
import random
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_TERMINAL_REBOOTED,
    COLOR_PLAYER,
    COLOR_EXIT_OPEN,
    COLOR_LASER_CORRUPT,
)


class Particle:
    """
    A single digital particle/spark.
    Has position, velocity, color, size, and lifetime.
    """

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: tuple[int, int, int],
        lifetime: int,
        size: float = 3.0,
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size

    def update(self) -> bool:
        """
        Updates physics.
        Returns False when particle has expired (lifetime <= 0).
        """
        self.x += self.vx
        self.y += self.vy
        # Gentle velocity damping (air resistance / deceleration)
        self.vx *= 0.91
        self.vy *= 0.91
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surface: pygame.Surface):
        """Renders particle with size decay and fade."""
        if self.lifetime <= 0:
            return

        progress = self.lifetime / self.max_lifetime
        current_size = max(1.0, self.size * progress)
        half_size = current_size / 2.0

        # Draw digital pixel shard
        rect = pygame.Rect(
            int(self.x - half_size),
            int(self.y - half_size),
            max(1, int(current_size)),
            max(1, int(current_size)),
        )
        pygame.draw.rect(surface, self.color, rect)


class GlitchBit:
    """
    An ambient floating fragment of corrupted data code.
    Gently drifts upward with occasional horizontal micro-twitches and flicker.
    """

    def __init__(self, x: float, y: float, color: tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-0.25, 0.25)
        self.vy = random.uniform(-0.5, -1.2)  # Upward ambient float
        self.lifetime = random.randint(55, 95)
        self.max_lifetime = self.lifetime
        self.size = random.choice([2, 2, 3, 3, 4])

    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

        # Occasional digital twitch / jitter (8% chance per frame)
        if random.random() < 0.08:
            self.x += random.choice([-2, -1, 1, 2])

        return self.lifetime > 0

    def draw(self, surface: pygame.Surface):
        if self.lifetime <= 0:
            return

        # Digital flicker shimmer (briefly invisible on occasional frames)
        if random.random() < 0.10:
            return

        rect = pygame.Rect(int(self.x), int(self.y), self.size, self.size)
        pygame.draw.rect(surface, self.color, rect)


class ParticleSystem:
    """
    Manages active visual effects:
    - Radial reboot bursts (sparking digital bits when servers restore)
    - Ambient glitch drift in the corrupted dimension
    """

    # Vibrant terminal reboot color palette: neon green, electric cyan, quantum gold, pure white
    REBOOT_COLORS = [
        COLOR_TERMINAL_REBOOTED,       # Neon green
        COLOR_EXIT_OPEN,               # Mint green
        COLOR_PLAYER,                  # Electric cyan
        (255, 255, 255),               # Pure white spark
        (245, 195, 65),                # Quantum amber
    ]

    # Corrupted dimension glitch palette: laser crimson, hot magenta, neon violet, dim amber
    GLITCH_COLORS = [
        COLOR_LASER_CORRUPT,           # (255, 45, 85)
        (255, 65, 125),                # Hot magenta
        (190, 75, 235),                # Electric violet
        (245, 166, 35),                # Terminal amber
        (255, 255, 255),               # Glitch white
    ]

    def __init__(self):
        self.particles: list[Particle] = []
        self.glitch_bits: list[GlitchBit] = []

    def emit_reboot_burst(self, center_x: float, center_y: float, count: int = 28):
        """
        Spawns a radial explosion of fast-moving digital shards
        emanating outwards from the rebooted server terminal.
        """
        for _ in range(count):
            angle = random.uniform(0, 2.0 * math.pi)
            speed = random.uniform(2.5, 7.5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            color = random.choice(self.REBOOT_COLORS)
            lifetime = random.randint(22, 38)
            size = random.uniform(3.0, 5.0)

            self.particles.append(
                Particle(center_x, center_y, vx, vy, color, lifetime, size)
            )

    def update(self, is_corrupted: bool = False):
        """
        Advances all active particles:
        - Updates reboot sparks and removes dead ones.
        - Spawns & floats ambient glitch bits when is_corrupted is True.
        - Clears glitch bits when returning to Normal reality.
        """
        # 1. Update reboot sparks
        self.particles = [p for p in self.particles if p.update()]

        # 2. Update ambient corrupted glitch bits
        if is_corrupted:
            # Maintain a cloud of ~32 active floating fragments
            if len(self.glitch_bits) < 32 and random.random() < 0.50:
                gx = random.uniform(16, SCREEN_WIDTH - 16)
                # If cloud is thin, spawn throughout; otherwise spawn from bottom edge
                gy = (
                    random.uniform(32, SCREEN_HEIGHT - 32)
                    if len(self.glitch_bits) < 12
                    else random.uniform(SCREEN_HEIGHT - 70, SCREEN_HEIGHT - 10)
                )
                color = random.choice(self.GLITCH_COLORS)
                self.glitch_bits.append(GlitchBit(gx, gy, color))

            self.glitch_bits = [bit for bit in self.glitch_bits if bit.update()]
        else:
            # Immediately clear glitch bits in the clean Normal dimension
            if self.glitch_bits:
                self.glitch_bits.clear()

    def draw(self, surface: pygame.Surface):
        """Draws ambient glitch bits and active particles onto the surface."""
        for bit in self.glitch_bits:
            bit.draw(surface)
        for p in self.particles:
            p.draw(surface)

    def clear(self):
        """Removes all active particles and glitch bits."""
        self.particles.clear()
        self.glitch_bits.clear()
