from __future__ import annotations
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_TEXT,
    COLOR_TERMINAL_OFF,
    COLOR_HAZARD_RED,
)
from src.input_handler import Action
from src.scenes.base import Scene


class PauseScene(Scene):
    """
    Pause overlay:
    Draws over the frozen game screen, offering Resume, Restart, or Quit.
    """
    def __init__(self, game, background_game_scene):
        super().__init__(game)
        self.background_game_scene = background_game_scene
        self.title_font = pygame.font.SysFont("monospace", 28, bold=True)
        self.option_font = pygame.font.SysFont("monospace", 18, bold=True)

        # Performance optimization: pre-render static texts and overlay surface
        self.dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.dim_surface.fill((0, 0, 0, 180))

        self.header_surf = self.title_font.render("SYSTEM PAUSED", True, COLOR_TERMINAL_OFF)
        self.opt1_surf = self.option_font.render("[ESC / A]  Resume", True, COLOR_TEXT)
        self.opt2_surf = self.option_font.render("[R / X]    Restart Sector", True, COLOR_TEXT)
        self.opt3_surf = self.option_font.render("[L]        Sector Select", True, (130, 180, 255))
        self.opt4_surf = self.option_font.render("[Q / B]    Quit to Title", True, COLOR_HAZARD_RED)

    def handle_events(self, events: list[pygame.event.Event], actions: list[Action]):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                from src.scenes.level_select_scene import LevelSelectScene
                self.game.change_scene(LevelSelectScene(self.game))
                return

        for action in actions:
            # ESC, Start, or A resumes gameplay
            if action in (Action.PAUSE, Action.CONFIRM):
                self.game.pop_scene()
                return
            # R or X button restarts the level
            elif action == Action.RESTART:
                self.background_game_scene.restart_level()
                self.game.pop_scene()
                return
            # Q or B button quits back to the title screen
            elif action == Action.CANCEL:
                from src.scenes.title_scene import TitleScene
                self.game.change_scene(TitleScene(self.game))
                return

    def draw(self, screen: pygame.Surface):
        # 1. Draw the game scene underneath so it stays visible behind the pause overlay
        self.background_game_scene.draw(screen)

        # 2. Semi-transparent black tint
        screen.blit(self.dim_surface, (0, 0))

        # 3. Pause menu text
        center_x = SCREEN_WIDTH // 2
        screen.blit(self.header_surf, (center_x - self.header_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 90))
        screen.blit(self.opt1_surf, (center_x - self.opt1_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(self.opt2_surf, (center_x - self.opt2_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 15))
        screen.blit(self.opt3_surf, (center_x - self.opt3_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(self.opt4_surf, (center_x - self.opt4_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 85))
