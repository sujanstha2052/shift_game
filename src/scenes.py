import sys
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    TILE_SIZE,
    COLOR_GRID_LINE,
    COLOR_TEXT,
    COLOR_PLAYER,
    COLOR_TERMINAL_REBOOTED,
)
from src.level import Level
from src.player import Player
from src.levels_data import LEVELS
from src.input_handler import Action


class Scene:
    """
    Base Scene class that all scenes inherit from.
    """
    def __init__(self, game):
        self.game = game  # Gives each scene access to the main Game object

    def handle_events(self, events: list[pygame.event.Event], actions: list[Action]):
        """Handle player actions or raw events for this scene."""
        pass

    def update(self):
        """Update game physics, animations, or logic."""
        pass

    def draw(self, screen: pygame.Surface):
        """Draw everything for this scene to the screen."""
        pass


# =============================================================================
# 1. TITLE SCENE
# =============================================================================
class TitleScene(Scene):
    """
    The main menu / introductory terminal screen.
    """
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont("monospace", 36, bold=True)
        self.sub_font = pygame.font.SysFont("monospace", 16)
        self.instruction_font = pygame.font.SysFont("monospace", 18, bold=True)
        
        self.blink_timer = 0
        self.show_text = True

    def handle_events(self, events: list[pygame.event.Event], actions: list[Action]):
        for action in actions:
            if action == Action.CONFIRM:
                # Start game! (Enter / Space on keyboard, or 'A' button on Gamepad)
                self.game.change_scene(GameScene(self.game, level_index=0))
                return
            elif action in (Action.PAUSE, Action.CANCEL):
                # Quit game (ESC / Q on keyboard, or 'B' on Gamepad)
                self.game.running = False
                return

    def update(self):
        self.blink_timer += 1
        if self.blink_timer >= 30:
            self.show_text = not self.show_text
            self.blink_timer = 0

    def draw(self, screen: pygame.Surface):
        screen.fill((16, 20, 28))  # Dark terminal slate

        # Main Title
        title_surf = self.title_font.render("SHIFT / RETURN", True, COLOR_PLAYER)
        tagline_surf = self.sub_font.render(
            "OmniCorp Data Center - Graveyard Shift", True, (150, 165, 185)
        )
        screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 140))
        screen.blit(tagline_surf, (SCREEN_WIDTH // 2 - tagline_surf.get_width() // 2, 195))

        # Instructions Box (showing both keyboard & controller hints)
        ctrl1 = self.sub_font.render("[WASD / D-Pad]     : Move Operator", True, COLOR_TEXT)
        ctrl2 = self.sub_font.render("[SHIFT / Bumpers]  : Phase Dimension", True, (245, 166, 35))
        ctrl3 = self.sub_font.render("[Goal]             : Reboot servers & reach exit", True, COLOR_TERMINAL_REBOOTED)
        screen.blit(ctrl1, (SCREEN_WIDTH // 2 - 180, 260))
        screen.blit(ctrl2, (SCREEN_WIDTH // 2 - 180, 290))
        screen.blit(ctrl3, (SCREEN_WIDTH // 2 - 180, 320))

        # Flashing Start Prompt
        if self.show_text:
            start_surf = self.instruction_font.render(
                "PRESS [ENTER / A] TO CLOCK IN", True, (52, 211, 153)
            )
            screen.blit(
                start_surf, (SCREEN_WIDTH // 2 - start_surf.get_width() // 2, 420)
            )


# =============================================================================
# 2. GAME SCENE (Active Gameplay)
# =============================================================================
class GameScene(Scene):
    """
    Active gameplay scene:
    Receives high-level Actions (Action.UP, Action.SHIFT, etc.)
    regardless of input device.
    """
    def __init__(self, game, level_index: int = 0):
        super().__init__(game)
        self.level_index = level_index
        self.level = Level(self.level_index)
        start_x, start_y = self.level.player_start
        self.player = Player(start_x, start_y)
        self.hud_font = pygame.font.SysFont("monospace", 16, bold=True)

    def restart_level(self):
        """Quick restart of current puzzle."""
        self.level = Level(self.level_index)
        start_x, start_y = self.level.player_start
        self.player.reset_position(start_x, start_y)

    def handle_events(self, events: list[pygame.event.Event], actions: list[Action]):
        for action in actions:
            # 1. Pause
            if action == Action.PAUSE:
                self.game.push_scene(PauseScene(self.game, self))
                return

            # 2. Quick Restart
            elif action == Action.RESTART:
                self.restart_level()
                return

            # 3. Dimension Shift
            elif action == Action.SHIFT:
                self.level.toggle_shift(self.player.grid_x, self.player.grid_y)

            # 4. Movement
            elif action == Action.UP:
                self.player.move(0, -1, self.level)
            elif action == Action.DOWN:
                self.player.move(0, 1, self.level)
            elif action == Action.LEFT:
                self.player.move(-1, 0, self.level)
            elif action == Action.RIGHT:
                self.player.move(1, 0, self.level)

    def update(self):
        self.level.update(self.player.grid_x, self.player.grid_y)

        # Check if the player stepped into the open exit gateway
        if self.level.is_won:
            self.game.change_scene(LevelClearScene(self.game, self.level_index))

    def draw(self, screen: pygame.Surface):
        # 1. Level tiles (walls & background)
        self.level.draw(screen)

        # 2. Grid lines
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(screen, COLOR_GRID_LINE, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(screen, COLOR_GRID_LINE, (0, y), (SCREEN_WIDTH, y))

        # 3. Player
        self.player.draw(screen)

        # 4. HUD
        rebooted = sum(1 for t in self.level.terminals if t.rebooted)
        total = len(self.level.terminals)
        dim_name = "CORRUPTED" if self.level.is_corrupted else "NORMAL"
        text = f"{self.level.name} | [{dim_name}] | Servers: {rebooted}/{total} | [R: Restart, ESC: Pause]"
        hud_surf = self.hud_font.render(text, True, COLOR_TEXT)
        screen.blit(hud_surf, (16, 12))


# =============================================================================
# 3. PAUSE SCENE (Overlay)
# =============================================================================
class PauseScene(Scene):
    """
    Pause overlay:
    Draws over the frozen game screen, offering Resume, Restart, or Quit.
    """
    def __init__(self, game, background_game_scene: GameScene):
        super().__init__(game)
        self.background_game_scene = background_game_scene
        self.title_font = pygame.font.SysFont("monospace", 28, bold=True)
        self.option_font = pygame.font.SysFont("monospace", 18, bold=True)

    def handle_events(self, events: list[pygame.event.Event], actions: list[Action]):
        for action in actions:
            # ESC or Start or A resumes gameplay
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
                self.game.change_scene(TitleScene(self.game))
                return

    def draw(self, screen: pygame.Surface):
        # 1. Draw the game scene underneath so it stays visible behind the pause overlay
        self.background_game_scene.draw(screen)

        # 2. Semi-transparent black tint
        dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surface.fill((0, 0, 0, 180))
        screen.blit(dim_surface, (0, 0))

        # 3. Pause menu text
        header = self.title_font.render("SYSTEM PAUSED", True, (245, 166, 35))
        opt1 = self.option_font.render("[ESC / A]  Resume", True, COLOR_TEXT)
        opt2 = self.option_font.render("[R / X]    Restart Sector", True, COLOR_TEXT)
        opt3 = self.option_font.render("[Q / B]    Quit to Title", True, (240, 90, 90))

        center_x = SCREEN_WIDTH // 2
        screen.blit(header, (center_x - header.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        screen.blit(opt1, (center_x - opt1.get_width() // 2, SCREEN_HEIGHT // 2 - 10))
        screen.blit(opt2, (center_x - opt2.get_width() // 2, SCREEN_HEIGHT // 2 + 25))
        screen.blit(opt3, (center_x - opt3.get_width() // 2, SCREEN_HEIGHT // 2 + 60))


# =============================================================================
# 4. LEVEL CLEAR SCENE
# =============================================================================
class LevelClearScene(Scene):
    """
    Celebration screen after reaching the unlocked exit.
    """
    def __init__(self, game, completed_level_index: int):
        super().__init__(game)
        self.completed_level_index = completed_level_index
        self.is_final = (self.completed_level_index == len(LEVELS) - 1)
        self.font = pygame.font.SysFont("monospace", 22, bold=True)
        self.sub_font = pygame.font.SysFont("monospace", 16)

    def handle_events(self, events: list[pygame.event.Event], actions: list[Action]):
        for action in actions:
            if action == Action.CONFIRM:
                if self.is_final:
                    self.game.change_scene(TitleScene(self.game))
                else:
                    next_idx = self.completed_level_index + 1
                    self.game.change_scene(GameScene(self.game, level_index=next_idx))
                return
            elif action in (Action.PAUSE, Action.CANCEL):
                self.game.change_scene(TitleScene(self.game))
                return

    def draw(self, screen: pygame.Surface):
        screen.fill((18, 22, 32))

        if self.is_final:
            header = self.font.render("ALL SERVERS RESTORED! SHIFT COMPLETE!", True, (52, 211, 153))
            sub = self.sub_font.render("Press [ENTER / A] to return to Title Screen", True, COLOR_TEXT)
        else:
            header = self.font.render("SECTOR CLEARED! ACCESS GRANTED", True, (52, 211, 153))
            sub = self.sub_font.render(
                f"Press [ENTER / A] to proceed to Sector {self.completed_level_index + 2:02d}", True, COLOR_TEXT
            )

        screen.blit(header, (SCREEN_WIDTH // 2 - header.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
