import pygame


def create_crt_overlay(width: int, height: int) -> pygame.Surface:
    """
    Pre-renders a reusable CRT scanline and subtle vignette overlay surface.
    - Horizontal scanlines: alternate lines with subtle dark alpha (32/255).
    - Vignette: soft corner shading giving a classic curved CRT terminal look.
    Pre-rendering once ensures zero performance impact at 60 FPS.
    """
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)

    # 1. Subtle horizontal scanlines
    scanline_color = (0, 0, 0, 30)
    for y in range(0, height, 2):
        pygame.draw.line(overlay, scanline_color, (0, y), (width, y), 1)

    # 2. Outer CRT screen bezel / vignette shading
    pygame.draw.rect(overlay, (0, 0, 0, 80), (0, 0, width, height), width=3, border_radius=8)
    pygame.draw.rect(overlay, (0, 0, 0, 45), (3, 3, width - 6, height - 6), width=2, border_radius=6)
    pygame.draw.rect(overlay, (0, 0, 0, 20), (5, 5, width - 10, height - 10), width=2, border_radius=4)

    return overlay
