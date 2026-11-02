import sys
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    TILE_SIZE,
    FPS,
    TITLE,
    COLOR_GRID_LINE,
    COLOR_TEXT,
)
from src.level import Level
from src.player import Player
from src.levels_data import LEVELS

def draw_grid_lines(surface: pygame.Surface):
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        pygame.draw.line(surface, COLOR_GRID_LINE, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
        pygame.draw.line(surface, COLOR_GRID_LINE, (0, y), (SCREEN_WIDTH, y))

def draw_hud(surface: pygame.Surface, font: pygame.font.Font, level: Level):
    rebooted = sum(1 for t in level.terminals if t.rebooted)
    total = len(level.terminals)
    dim_name = "CORRUPTED" if level.is_corrupted else "NORMAL"

    text = f"{level.name} | [{dim_name}] | Servers: {rebooted}/{total}"
    hud_surf = font.render(text, True, COLOR_TEXT)
    surface.blit(hud_surf, (16, 12))

def draw_level_clear(surface: pygame.Surface, font: pygame.font.Font, is_final: bool):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))

    if is_final:
        header = font.render("ALL SERVERS RESTORED! SYSTEM OPERATIONAL!", True, (52, 211, 153))
        sub = font.render("Press ENTER to play again or ESC to exit", True, COLOR_TEXT)
    else:
        header = font.render("SECTOR CLEARED!", True, (52, 211, 153))
        sub = font.render("Press ENTER to proceed to the next sub-level", True, COLOR_TEXT)

    surface.blit(header, (SCREEN_WIDTH // 2 - header.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
    surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, SCREEN_HEIGHT // 2 + 15))

def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 16, bold=True)
    modal_font = pygame.font.SysFont("monospace", 20, bold=True)

    current_level_idx = 0
    level = Level(current_level_idx)
    start_x, start_y = level.player_start
    player = Player(start_x, start_y)

    game_cleared = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Handle level advancement or restart
                if level.is_won:
                    if event.key == pygame.K_RETURN:
                        if current_level_idx + 1 < len(LEVELS):
                            current_level_idx += 1
                            level.load_level(current_level_idx)
                            px, py = level.player_start
                            player.reset_position(px, py)
                        else:
                            # Loop back to level 1
                            current_level_idx = 0
                            level.load_level(current_level_idx)
                            px, py = level.player_start
                            player.reset_position(px, py)
                            game_cleared = False
                    continue

                # In-game controls
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    level.toggle_shift(player.grid_x, player.grid_y)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    player.move(0, -1, level)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    player.move(0, 1, level)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    player.move(-1, 0, level)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    player.move(1, 0, level)

        # Update interactions
        if not level.is_won:
            level.update(player.grid_x, player.grid_y)

        # Render
        level.draw(screen)
        draw_grid_lines(screen)
        player.draw(screen)
        draw_hud(screen, font, level)

        if level.is_won:
            is_final_level = (current_level_idx == len(LEVELS) - 1)
            draw_level_clear(screen, modal_font, is_final_level)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()