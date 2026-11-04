import random
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    TILE_SIZE,
    COLOR_GRID_LINE,
    COLOR_TEXT,
    COLOR_HAZARD_RED,
)
from src.level import Level
from src.player import Player
from src.levels_data import LEVELS
from src.input_handler import Action
from src.scenes.base import Scene, StateSnapshot


class GameScene(Scene):
    """
    Active gameplay scene:
    Receives high-level Actions (Action.UP, Action.SHIFT, Action.UNDO, etc.)
    and coordinates player physics, reality shifting, sentinels, and rendering.
    """
    def __init__(self, game, level_index: int = 0):
        super().__init__(game)
        self.level_index = level_index
        self.level = Level(self.level_index)
        start_x, start_y = self.level.player_start
        self.player = Player(start_x, start_y)
        self.hud_font = pygame.font.SysFont("monospace", 16, bold=True)
        self.alert_font = pygame.font.SysFont("monospace", 22, bold=True)

        # Undo history stack
        self.history: list[StateSnapshot] = []

        # Screen Shake & Rejection Feedback
        self.shake_timer = 0
        self.shake_magnitude = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.red_flash_timer = 0
        self.blocked_shift_pos: tuple[int, int] | None = None

        # Dimension Shift Transition Juice
        self.shift_transition_timer = 0
        self.shift_max_frames = 12

        # Daemon Detection State
        self.is_caught = False

        # --- Performance Optimizations: Persistent Surfaces ---
        self.render_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.beam_surf = pygame.Surface((SCREEN_WIDTH, 8), pygame.SRCALPHA)
        self.hazard_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.hazard_surf.fill((255, 30, 30, 100))

        # Breach overlay pre-renders
        self.breach_overlay_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.breach_overlay_surf.fill((30, 0, 10, 200))
        self.breach_msg1 = self.alert_font.render("SECURITY BREACH: DAEMON INTERCEPT!", True, COLOR_HAZARD_RED)
        self.breach_msg2 = self.hud_font.render("Press [Z] to Rewind Move  |  Press [R] to Restart Sector", True, COLOR_TEXT)

        # Start synchronized dual-layer ambient BGM
        self.game.audio.start_music()
        self.game.audio.set_dimension_music(self.level.is_corrupted)

    def trigger_shift_rejection(self):
        """Triggers screen shake, red strobe flash, and buzzer on invalid shift."""
        self.shake_timer = 10
        self.shake_magnitude = 6
        self.red_flash_timer = 12
        self.blocked_shift_pos = (self.player.grid_x, self.player.grid_y)
        self.game.audio.play_error_buzz()

    def restart_level(self):
        """Quick restart of current puzzle."""
        self.is_caught = False
        self.load_level(self.level_index)

    def load_level(self, index: int):
        """Jumps directly to a specified level index (resets position and undo stack)."""
        self.level_index = index % len(LEVELS)
        self.level = Level(self.level_index)
        start_x, start_y = self.level.player_start
        self.player.reset_position(start_x, start_y)
        self.history.clear()
        self.is_caught = False

    def save_snapshot(self):
        """Saves current state to history before a move/shift executes."""
        snapshot = StateSnapshot(
            player_x=self.player.grid_x,
            player_y=self.player.grid_y,
            facing_x=self.player.facing_x,
            facing_y=self.player.facing_y,
            is_corrupted=self.level.is_corrupted,
            terminals_rebooted=tuple(t.rebooted for t in self.level.terminals),
            blocks_state=tuple((b.grid_x, b.grid_y) for b in self.level.blocks),
            daemons_state=tuple((d.grid_x, d.grid_y, d.point_index, d.direction) for d in self.level.daemons),
        )
        self.history.append(snapshot)

    def undo(self):
        """Reverts to the most recent state in the history stack."""
        if not self.history or self.player.is_moving:
            return

        snapshot = self.history.pop()
        self.is_caught = False

        # 1. Restore Player position and orientation
        self.player.reset_position(snapshot.player_x, snapshot.player_y)
        self.player.facing_x = snapshot.facing_x
        self.player.facing_y = snapshot.facing_y

        # 2. Restore Active Dimension
        self.level.is_corrupted = snapshot.is_corrupted

        # 3. Restore Terminal reboot statuses
        for terminal, was_rebooted in zip(self.level.terminals, snapshot.terminals_rebooted):
            terminal.rebooted = was_rebooted

        # 4. Restore RAM Blocks
        for block, (bx, by) in zip(self.level.blocks, snapshot.blocks_state):
            block.reset_position(bx, by)

        # 5. Restore Daemons
        for daemon, (dx, dy, idx, direct) in zip(self.level.daemons, snapshot.daemons_state):
            daemon.reset_state(dx, dy, idx, direct)

        # 6. Restore BGM dimension track
        self.game.audio.set_dimension_music(self.level.is_corrupted)

        # 7. Play audio rewind blip
        self.game.audio.play_undo()

    def try_move_player(self, dx: int, dy: int):
        """Attempts to move the player or push RAM blocks; handles bump & push sounds."""
        if self.player.is_moving or self.is_caught:
            return

        new_x = self.player.grid_x + dx
        new_y = self.player.grid_y + dy

        # 1. Wall Obstruction: cannot move or push
        if self.level.is_wall(new_x, new_y):
            self.player.move(dx, dy, self.level)
            self.game.audio.play_bump()
            return

        # 2. Active Laser Obstruction: lethal barrier blocks player
        if self.level.is_laser_active_at(new_x, new_y):
            self.player.move(dx, dy, self.level)
            self.game.audio.play_error_buzz()
            return

        # 3. RAM Block: check if push is possible
        block = self.level.get_block_at(new_x, new_y)
        if block is not None:
            # Check if tile behind block is clear
            if self.level.try_push_block(block, dx, dy):
                # Successful push! Save undo, move player into vacated tile, play clunk
                self.save_snapshot()
                self.player.move(dx, dy, self.level)
                self.game.audio.play_block_push()

                # Patrol daemons take 1 step if in Corrupted Dimension
                if self.level.is_corrupted and self.level.step_daemons():
                    self.game.audio.play_daemon_step()
            else:
                # Block is blocked by a wall or other obstacle
                self.player.move(dx, dy, self.level)
                self.game.audio.play_bump()
            return

        # 4. Open Floor: standard movement
        self.save_snapshot()
        self.player.move(dx, dy, self.level)

        # Patrol daemons take 1 step if in Corrupted Dimension
        if self.level.is_corrupted and self.level.step_daemons():
            self.game.audio.play_daemon_step()

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

        # If intercepted by a daemon, restrict actions to Undo, Restart, or Exit
        if self.is_caught:
            for action in actions:
                if action == Action.UNDO:
                    self.undo()
                    return
                elif action == Action.RESTART:
                    self.restart_level()
                    return
                elif action in (Action.PAUSE, Action.CANCEL):
                    from src.scenes.title_scene import TitleScene
                    self.game.change_scene(TitleScene(self.game))
                    return
            return

        for action in actions:
            # 1. Pause
            if action == Action.PAUSE:
                from src.scenes.pause_scene import PauseScene
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
                        self.shift_transition_timer = self.shift_max_frames
                        self.game.audio.play_shift_whoosh()
                        # Crossfade BGM layer to matching reality in-beat!
                        self.game.audio.set_dimension_music(self.level.is_corrupted)

                        # Sentinels advance when inside the Corrupted Dimension
                        if self.level.is_corrupted and self.level.step_daemons():
                            self.game.audio.play_daemon_step()
                    else:
                        # Wall obstruction! Trigger screen shake, red strobe, and error buzzer
                        self.trigger_shift_rejection()

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

        # 2. Update screen shake
        if self.shake_timer > 0:
            self.shake_timer -= 1
            self.shake_offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            self.shake_offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0

        # 3. Update red flash strobe
        if self.red_flash_timer > 0:
            self.red_flash_timer -= 1
        else:
            self.blocked_shift_pos = None

        # 4. Update dimension transition timer
        if self.shift_transition_timer > 0:
            self.shift_transition_timer -= 1

        # 5. Check puzzle interactions (plates, servers, exit door)
        rebooted, plate_clicked = self.level.update(self.player.grid_x, self.player.grid_y)
        if rebooted:
            self.game.audio.play_reboot()
        if plate_clicked:
            self.game.audio.play_switch_click()

        # 6. Check daemon collision / intercept
        if not self.is_caught and self.level.is_daemon_at(self.player.grid_x, self.player.grid_y):
            self.is_caught = True
            self.game.audio.play_alarm()
            self.shake_timer = 14
            self.shake_magnitude = 8
            self.red_flash_timer = 16

        # 7. Check if the player stepped into the open exit gateway
        if not self.is_caught and self.level.is_won:
            from src.scenes.level_clear_scene import LevelClearScene
            self.game.change_scene(LevelClearScene(self.game, self.level_index))

    def _draw_grid(self, surface: pygame.Surface):
        """Draws subtle grid lines indicating the digital server matrix."""
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(surface, COLOR_GRID_LINE, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(surface, COLOR_GRID_LINE, (0, y), (SCREEN_WIDTH, y))

    def _draw_shift_transition(self, surface: pygame.Surface):
        """Renders glitch slice displacement, color flash, and sweeping scanline beam."""
        if self.shift_transition_timer <= 0:
            return

        t = 1.0 - (self.shift_transition_timer / self.shift_max_frames)

        # 1. Horizontal Glitch Slice Displacement (Chromatic tear)
        if self.shift_transition_timer > 3:
            for _ in range(3):
                slice_y = random.randint(0, SCREEN_HEIGHT - 30)
                slice_h = random.randint(8, 24)
                slice_offset = random.choice([-10, -6, 6, 10])
                strip = surface.subsurface((0, slice_y, SCREEN_WIDTH, slice_h)).copy()
                surface.blit(strip, (slice_offset, slice_y))

        # 2. Dimension Color Flash (Cyan when entering Normal, Magenta when entering Corrupt)
        flash_color = (190, 45, 85) if self.level.is_corrupted else (60, 160, 240)
        alpha = int((self.shift_transition_timer / self.shift_max_frames) * 75)
        self.flash_surf.fill((*flash_color, alpha))
        surface.blit(self.flash_surf, (0, 0))

        # 3. Sweeping Horizontal Scanline Beam
        beam_y = int(t * SCREEN_HEIGHT)
        beam_color = (255, 120, 160) if self.level.is_corrupted else (180, 230, 255)
        self.beam_surf.fill((*beam_color, 180))
        surface.blit(self.beam_surf, (0, max(0, beam_y - 4)))
        pygame.draw.line(surface, (255, 255, 255), (0, beam_y), (SCREEN_WIDTH, beam_y), width=2)

    def _draw_hazard_box(self, surface: pygame.Surface):
        """Draws a red hazard warning box over the player tile if a shift was blocked."""
        if not (self.blocked_shift_pos and self.red_flash_timer > 0):
            return
        bx, by = self.blocked_shift_pos
        hazard_rect = pygame.Rect(bx * TILE_SIZE, by * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        surface.blit(self.hazard_surf, (bx * TILE_SIZE, by * TILE_SIZE))
        pygame.draw.rect(surface, (255, 60, 60), hazard_rect, width=3, border_radius=4)

    def _draw_red_flash(self, surface: pygame.Surface):
        """Draws a screen-wide red strobe flash overlay on illegal shifts or alerts."""
        if self.red_flash_timer <= 0:
            return
        alpha = int((self.red_flash_timer / 12) * 90)
        self.flash_surf.fill((255, 20, 20, alpha))
        surface.blit(self.flash_surf, (0, 0))

    def _draw_hud(self, screen: pygame.Surface):
        """Draws the top heads-up display with sector name, dimension, and server status."""
        rebooted = sum(1 for t in self.level.terminals if t.rebooted)
        total = len(self.level.terminals)
        dim_name = "CORRUPTED" if self.level.is_corrupted else "NORMAL"
        text = f"{self.level.name} | [{dim_name}] | Servers: {rebooted}/{total} | [Z: Undo, R: Restart, ESC: Pause]"
        hud_surf = self.hud_font.render(text, True, COLOR_TEXT)
        screen.blit(hud_surf, (16 + self.shake_offset_x, 12 + self.shake_offset_y))

    def _draw_breach_overlay(self, screen: pygame.Surface):
        """Renders the alert message when a daemon intercepts the player."""
        if not self.is_caught:
            return
        screen.blit(self.breach_overlay_surf, (0, 0))
        screen.blit(self.breach_msg1, (SCREEN_WIDTH // 2 - self.breach_msg1.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        screen.blit(self.breach_msg2, (SCREEN_WIDTH // 2 - self.breach_msg2.get_width() // 2, SCREEN_HEIGHT // 2 + 15))

    def draw(self, screen: pygame.Surface):
        # 1. Level tiles (walls & floor) onto internal surface
        self.level.draw(self.render_surf)

        # 2. Grid lines
        self._draw_grid(self.render_surf)

        # 3. Dimension Shift Transition (Chromatic Tear & Scanline Beam)
        self._draw_shift_transition(self.render_surf)

        # 4. Blocked shift hazard highlight
        self._draw_hazard_box(self.render_surf)

        # 5. Player sprite & directional eye visor
        self.player.draw(self.render_surf)

        # 6. Red screen flash overlay
        self._draw_red_flash(self.render_surf)

        # 7. Blit internal surface onto screen with camera shake offset
        screen.fill((10, 10, 15))
        screen.blit(self.render_surf, (self.shake_offset_x, self.shake_offset_y))

        # 8. HUD
        self._draw_hud(screen)

        # 9. Security Breach Overlay
        self._draw_breach_overlay(screen)
