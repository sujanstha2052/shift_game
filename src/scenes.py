from dataclasses import dataclass
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


@dataclass
class StateSnapshot:
    """A frozen snapshot of game state at a specific point in time."""
    player_x: int
    player_y: int
    facing_x: int
    facing_y: int
    is_corrupted: bool
    terminals_rebooted: tuple[bool, ...]


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
        # Check raw keyboard events for shortcut 'L'
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                self.game.change_scene(LevelSelectScene(self.game))
                return

        for action in actions:
            if action == Action.CONFIRM:
                # Start game at Level 0
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

        # Main Title
        title_surf = self.title_font.render("SHIFT / RETURN", True, COLOR_PLAYER)
        tagline_surf = self.sub_font.render(
            "OmniCorp Data Center - Graveyard Shift", True, (150, 165, 185)
        )
        screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 140))
        screen.blit(tagline_surf, (SCREEN_WIDTH // 2 - tagline_surf.get_width() // 2, 195))

        # Instructions Box (showing controls & sector select)
        ctrl1 = self.sub_font.render("[WASD / D-Pad]     : Move Operator", True, COLOR_TEXT)
        ctrl2 = self.sub_font.render("[SHIFT / Bumpers]  : Phase Dimension", True, (245, 166, 35))
        ctrl3 = self.sub_font.render("[Goal]             : Reboot servers & reach exit", True, COLOR_TERMINAL_REBOOTED)
        ctrl4 = self.sub_font.render("[L Key]            : Sector Select Menu", True, (130, 180, 255))
        screen.blit(ctrl1, (SCREEN_WIDTH // 2 - 180, 250))
        screen.blit(ctrl2, (SCREEN_WIDTH // 2 - 180, 275))
        screen.blit(ctrl3, (SCREEN_WIDTH // 2 - 180, 300))
        screen.blit(ctrl4, (SCREEN_WIDTH // 2 - 180, 325))

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
        # Undo history stack
        self.history: list[StateSnapshot] = []

    def restart_level(self):
        """Quick restart of current puzzle."""
        self.load_level(self.level_index)

    def load_level(self, index: int):
        """Jumps directly to a specified level index (resets position and undo stack)."""
        self.level_index = index % len(LEVELS)
        self.level = Level(self.level_index)
        start_x, start_y = self.level.player_start
        self.player.reset_position(start_x, start_y)
        self.history.clear()

    def save_snapshot(self):
        """Saves current state to history before a move/shift executes."""
        snapshot = StateSnapshot(
            player_x=self.player.grid_x,
            player_y=self.player.grid_y,
            facing_x=self.player.facing_x,
            facing_y=self.player.facing_y,
            is_corrupted=self.level.is_corrupted,
            terminals_rebooted=tuple(t.rebooted for t in self.level.terminals),
        )
        self.history.append(snapshot)

    def undo(self):
        """Reverts to the most recent state in the history stack."""
        if not self.history or self.player.is_moving:
            return

        snapshot = self.history.pop()

        # 1. Restore Player position and orientation
        self.player.reset_position(snapshot.player_x, snapshot.player_y)
        self.player.facing_x = snapshot.facing_x
        self.player.facing_y = snapshot.facing_y

        # 2. Restore Active Dimension
        self.level.is_corrupted = snapshot.is_corrupted

        # 3. Restore Terminal reboot statuses
        for terminal, was_rebooted in zip(self.level.terminals, snapshot.terminals_rebooted):
            terminal.rebooted = was_rebooted

        # 4. Play audio rewind blip
        self.game.audio.play_undo()

    def try_move_player(self, dx: int, dy: int):
        """Attempts to move the player; saves undo state on success, or bumps on wall."""
        if self.player.is_moving:
            return

        new_x = self.player.grid_x + dx
        new_y = self.player.grid_y + dy

        if not self.level.is_solid(new_x, new_y):
            # Save undo snapshot BEFORE updating position
            self.save_snapshot()
            self.player.move(dx, dy, self.level)
        else:
            # Trigger wall bump and thump sound
            self.player.move(dx, dy, self.level)
            self.game.audio.play_bump()

    def handle_events(self, events: list[pygame.event.Event], actions: list[Action]):
        # Fast Developer / Playtester Hotkeys (N: Next Level, P: Prev Level, 1-9: Direct Jump)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.load_level((self.level_index + 1) % len(LEVELS))
                    return
                elif event.key == pygame.K_p:
                    self.load_level((self.level_index - 1) % len(LEVELS))
                    return
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    lvl_idx = event.key - pygame.K_1
                    if lvl_idx < len(LEVELS):
                        self.load_level(lvl_idx)
                        return

        for action in actions:
            # 1. Pause
            if action == Action.PAUSE:
                self.game.push_scene(PauseScene(self.game, self))
                return

            # 2. Quick Restart
            elif action == Action.RESTART:
                self.restart_level()
                return

            # 3. Undo Step
            elif action == Action.UNDO:
                self.undo()
                return

            # 4. Dimension Shift (only allowed when stationary)
            elif action == Action.SHIFT:
                if not self.player.is_moving:
                    if self.level.can_shift(self.player.grid_x, self.player.grid_y):
                        self.save_snapshot()
                        self.level.toggle_shift(self.player.grid_x, self.player.grid_y)

            # 5. Movement
            elif action == Action.UP:
                self.try_move_player(0, -1)
            elif action == Action.DOWN:
                self.try_move_player(0, 1)
            elif action == Action.LEFT:
                self.try_move_player(-1, 0)
            elif action == Action.RIGHT:
                self.try_move_player(1, 0)

    def update(self):
        # 1. Update player smooth sliding interpolation
        self.player.update()

        # 2. Check puzzle interactions (servers, exit door)
        self.level.update(self.player.grid_x, self.player.grid_y)

        # 3. Check if the player stepped into the open exit gateway
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
        text = f"{self.level.name} | [{dim_name}] | Servers: {rebooted}/{total} | [Z: Undo, R: Restart, ESC: Pause]"
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
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                self.game.change_scene(LevelSelectScene(self.game))
                return

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
        opt3 = self.option_font.render("[L]        Sector Select", True, (130, 180, 255))
        opt4 = self.option_font.render("[Q / B]    Quit to Title", True, (240, 90, 90))

        center_x = SCREEN_WIDTH // 2
        screen.blit(header, (center_x - header.get_width() // 2, SCREEN_HEIGHT // 2 - 90))
        screen.blit(opt1, (center_x - opt1.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(opt2, (center_x - opt2.get_width() // 2, SCREEN_HEIGHT // 2 + 15))
        screen.blit(opt3, (center_x - opt3.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(opt4, (center_x - opt4.get_width() // 2, SCREEN_HEIGHT // 2 + 85))


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


# =============================================================================
# 5. LEVEL / SECTOR SELECT SCENE
# =============================================================================
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

    def handle_events(self, events: list[pygame.event.Event], actions: list[Action]):
        for action in actions:
            # Navigate Up
            if action == Action.UP:
                self.selected_index = (self.selected_index - 1) % len(LEVELS)
            # Navigate Down
            elif action == Action.DOWN:
                self.selected_index = (self.selected_index + 1) % len(LEVELS)
            # Select / Start Level
            elif action == Action.CONFIRM:
                self.game.change_scene(GameScene(self.game, level_index=self.selected_index))
                return
            # Back to Title
            elif action in (Action.PAUSE, Action.CANCEL):
                self.game.change_scene(TitleScene(self.game))
                return

    def draw(self, screen: pygame.Surface):
        screen.fill((16, 20, 28))

        # Title
        header = self.title_font.render("SECTOR SELECT", True, COLOR_PLAYER)
        screen.blit(header, (SCREEN_WIDTH // 2 - header.get_width() // 2, 70))

        # Sector List
        start_y = 150
        for idx, lvl in enumerate(LEVELS):
            is_selected = (idx == self.selected_index)
            prefix = "> " if is_selected else "  "
            text = f"{prefix}Sector {lvl['id']:02d}: {lvl['name']}"

            color = (52, 211, 153) if is_selected else COLOR_TEXT
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
                pygame.draw.rect(screen, (52, 211, 153), box_rect, width=1, border_radius=4)

            screen.blit(item_surf, (SCREEN_WIDTH // 2 - 220, start_y + (idx * 45)))

        # Hint Footer
        hint = self.hint_font.render(
            "[UP/DOWN / D-Pad] Browse  |  [ENTER / A] Launch  |  [ESC / B] Back",
            True,
            (140, 155, 175),
        )
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 60))
