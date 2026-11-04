import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_TEXT,
    COLOR_PLAYER,
    COLOR_TERMINAL_OFF,
    COLOR_TERMINAL_REBOOTED,
    COLOR_EXIT_OPEN,
)
from src.input_handler import Action
from src.scenes.base import Scene


class TitleScene(Scene):
    """
    The main menu / introductory terminal screen.
    Displays controls, game lore, and the start prompt.
    """
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont("monospace", 36, bold=True)
        self.sub_font = pygame.font.SysFont("monospace", 16)
        self.instruction_font = pygame.font.SysFont("monospace", 18, bold=True)

        self.blink_timer = 0
        self.show_text = True

        # Pre-rendered static surfaces for performance optimization
        self.title_surf = self.title_font.render("SHIFT / RETURN", True, COLOR_PLAYER)
        self.tagline_surf = self.sub_font.render(
            "OmniCorp Data Center - Graveyard Shift", True, (150, 165, 185)
        )
        self.ctrl1 = self.sub_font.render("[WASD / D-Pad]     : Move Operator", True, COLOR_TEXT)
        self.ctrl2 = self.sub_font.render("[SHIFT / Bumpers]  : Phase Dimension", True, COLOR_TERMINAL_OFF)
        self.ctrl3 = self.sub_font.render("[Goal]             : Reboot servers & reach exit", True, COLOR_TERMINAL_REBOOTED)
        self.ctrl4 = self.sub_font.render("[L Key]            : Sector Select Menu", True, (130, 180, 255))
        self.start_surf = self.instruction_font.render(
            "PRESS [ENTER / A] TO CLOCK IN", True, COLOR_EXIT_OPEN
        )

    def handle_events(self, events: list[pygame.event.Event], actions: list[Action]):
        # Shortcut 'L' jumps directly to Sector Select
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                from src.scenes.level_select_scene import LevelSelectScene
                self.game.change_scene(LevelSelectScene(self.game))
                return

        for action in actions:
            if action == Action.CONFIRM:
                # Start game at Level 0
                from src.scenes.game_scene import GameScene
                self.game.change_scene(GameScene(self.game, level_index=0))
                return
            elif action in (Action.PAUSE, Action.CANCEL):
                # Quit game
                self.game.running = False
                return

    def update(self):
        self.blink_timer += 1
        if self.blink_timer >= 30:
            self.show_text = not self.show_text
            self.blink_timer = 0

    def draw(self, screen: pygame.Surface):
        screen.fill((16, 20, 28))  # Dark terminal slate

        # Main Title & Tagline
        screen.blit(self.title_surf, (SCREEN_WIDTH // 2 - self.title_surf.get_width() // 2, 140))
        screen.blit(self.tagline_surf, (SCREEN_WIDTH // 2 - self.tagline_surf.get_width() // 2, 195))

        # Instructions Box
        screen.blit(self.ctrl1, (SCREEN_WIDTH // 2 - 180, 250))
        screen.blit(self.ctrl2, (SCREEN_WIDTH // 2 - 180, 275))
        screen.blit(self.ctrl3, (SCREEN_WIDTH // 2 - 180, 300))
        screen.blit(self.ctrl4, (SCREEN_WIDTH // 2 - 180, 325))

        # Flashing Start Prompt
        if self.show_text:
            screen.blit(
                self.start_surf, (SCREEN_WIDTH // 2 - self.start_surf.get_width() // 2, 420)
            )
