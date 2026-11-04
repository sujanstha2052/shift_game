import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    COLOR_PLAYER,
    COLOR_EXIT_OPEN,
)
from src.input_handler import Action
from src.levels_data import LEVELS
from src.scenes.base import Scene


class LevelSelectScene(Scene):
    """
    Allows the player or playtester to select and jump directly to any sector.
    """
    def __init__(self, game):
        super().__init__(game)
        self.selected_index = 0
        self.title_font = pygame.font.SysFont("monospace", 28, bold=True)
        self.item_font = pygame.font.SysFont("monospace", 18, bold=True)
        self.hint_font = pygame.font.SysFont("monospace", 14)

        # Pre-render static headers and hints
        self.header_surf = self.title_font.render("SECTOR SELECT", True, COLOR_PLAYER)
        self.hint_surf = self.hint_font.render(
            "[UP/DOWN / D-Pad] Browse  |  [ENTER / A] Launch  |  [ESC / B] Back",
            True,
            COLOR_TEXT_DIM,
        )

    def handle_events(self, events: list[pygame.event.Event], actions: list[Action]):
        for action in actions:
            if action == Action.UP:
                self.selected_index = (self.selected_index - 1) % len(LEVELS)
            elif action == Action.DOWN:
                self.selected_index = (self.selected_index + 1) % len(LEVELS)
            elif action == Action.CONFIRM:
                from src.scenes.game_scene import GameScene
                self.game.change_scene(GameScene(self.game, level_index=self.selected_index))
                return
            elif action in (Action.PAUSE, Action.CANCEL):
                from src.scenes.title_scene import TitleScene
                self.game.change_scene(TitleScene(self.game))
                return

    def draw(self, screen: pygame.Surface):
        screen.fill((16, 20, 28))

        # Title
        screen.blit(self.header_surf, (SCREEN_WIDTH // 2 - self.header_surf.get_width() // 2, 70))

        # Sector List
        start_y = 150
        for idx, lvl in enumerate(LEVELS):
            is_selected = (idx == self.selected_index)
            prefix = "> " if is_selected else "  "
            text = f"{prefix}Sector {lvl['id']:02d}: {lvl['name']}"

            color = COLOR_EXIT_OPEN if is_selected else COLOR_TEXT
            item_surf = self.item_font.render(text, True, color)

            # Highlight box for selected item
            if is_selected:
                box_rect = pygame.Rect(
                    SCREEN_WIDTH // 2 - 240,
                    start_y + (idx * 45) - 4,
                    480,
                    32,
                )
                pygame.draw.rect(screen, (30, 45, 65), box_rect, border_radius=4)
                pygame.draw.rect(screen, COLOR_EXIT_OPEN, box_rect, width=1, border_radius=4)

            screen.blit(item_surf, (SCREEN_WIDTH // 2 - 220, start_y + (idx * 45)))

        # Hint Footer
        screen.blit(self.hint_surf, (SCREEN_WIDTH // 2 - self.hint_surf.get_width() // 2, SCREEN_HEIGHT - 60))
