import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_TEXT,
    COLOR_EXIT_OPEN,
)
from src.input_handler import Action
from src.levels_data import LEVELS
from src.scenes.base import Scene


class LevelClearScene(Scene):
    """
    Celebration screen after reaching the unlocked exit.
    Plays victory fanfare and transitions to the next level or title screen.
    """
    def __init__(self, game, completed_level_index: int):
        super().__init__(game)
        self.completed_level_index = completed_level_index
        self.is_final = (self.completed_level_index == len(LEVELS) - 1)
        self.font = pygame.font.SysFont("monospace", 22, bold=True)
        self.sub_font = pygame.font.SysFont("monospace", 16)

        # Pre-render texts for performance
        if self.is_final:
            self.header_surf = self.font.render("ALL SERVERS RESTORED! SHIFT COMPLETE!", True, COLOR_EXIT_OPEN)
            self.sub_surf = self.sub_font.render("Press [ENTER / A] to Clock Out", True, COLOR_TEXT)
        else:
            self.header_surf = self.font.render("SECTOR CLEARED! ACCESS GRANTED", True, COLOR_EXIT_OPEN)
            self.sub_surf = self.sub_font.render(
                f"Press [ENTER / A] to proceed to Sector {self.completed_level_index + 2:02d}", True, COLOR_TEXT
            )

        # Play victory fanfare and return music to normal
        self.game.audio.set_dimension_music(False)
        self.game.audio.play_victory_fanfare()

    def handle_events(self, events: list[pygame.event.Event], actions: list[Action]):
        for action in actions:
            if action == Action.CONFIRM:
                if self.is_final:
                    from src.scenes.ending_scene import EndingScene
                    self.game.change_scene(EndingScene(self.game))
                else:
                    from src.scenes.game_scene import GameScene
                    next_idx = self.completed_level_index + 1
                    self.game.change_scene(GameScene(self.game, level_index=next_idx))
                return
            elif action in (Action.PAUSE, Action.CANCEL):
                from src.scenes.title_scene import TitleScene
                self.game.change_scene(TitleScene(self.game))
                return

    def draw(self, screen: pygame.Surface):
        screen.fill((18, 22, 32))
        screen.blit(self.header_surf, (SCREEN_WIDTH // 2 - self.header_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        screen.blit(self.sub_surf, (SCREEN_WIDTH // 2 - self.sub_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
