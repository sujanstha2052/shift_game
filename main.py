import sys
import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, COLOR_BG_NORMAL, COLOR_BG_CORRUPT, COLOR_GRID_LINE, COLOR_TEXT

def main():
    # 1. Initialize all pygame sub-modules
    pygame.init()

    # 2. setup window and clock
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    running = True

    # 3. main game loop
    while running:
        # a. event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # b. update state ( game logic, movement, and shifts)

        # c. draw
        screen.fill(COLOR_BG_NORMAL)

        # filp the display buffer
        pygame.display.flip()

        # d. frame rate timing
        # restrict the loop to 60 frames per second
        clock.tick(FPS)

    # 4. cleanup and exit
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()