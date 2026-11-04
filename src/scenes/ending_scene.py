import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG_NORMAL,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    COLOR_PLAYER,
    COLOR_TERMINAL_OFF,
    COLOR_EXIT_OPEN,
)
from src.input_handler import Action
from src.scenes.base import Scene


class EndingScene(Scene):
    """
    The epilogue / clock-out screen shown upon completing all 12 mainframe sectors.
    Displays narrative closure, performance statistics, and graveyard shift evaluation.
    """

    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("monospace", 15)
        self.font_bold = pygame.font.SysFont("monospace", 15, bold=True)
        self.font_header = pygame.font.SysFont("monospace", 18, bold=True)
        self.prompt_font = pygame.font.SysFont("monospace", 16, bold=True)

        # Retrieve player stats tracked across the night shift
        moves = self.game.stats.get("moves", 0)
        shifts = self.game.stats.get("shifts", 0)
        reboots = self.game.stats.get("reboots", 0)

        # Script lines: (text, color, is_bold)
        self.script_data: list[tuple[str, tuple[int, int, int], bool]] = [
            (">>> OMNICORP EMPLOYEE LOGOUT TERMINAL v4.2.0 <<<", COLOR_PLAYER, True),
            ("TIME: 06:00:00 AM (DAWN)   |   STATUS: CORE STABILIZED", COLOR_EXIT_OPEN, True),
            ("INCIDENT #9904-QUANTUM-LEAK : RESOLVED & ARCHIVED", COLOR_TERMINAL_OFF, False),
            ("", COLOR_TEXT, False),
            ("DEBRIEFING: TO JUNIOR NIGHT OPERATOR", (240, 240, 250), True),
            ("--------------------------------------------------", (65, 80, 105), False),
            ("The memory breach is sealed. Reality layers merged.", COLOR_TEXT, False),
            ("The day shift engineers are arriving with coffee & donuts.", COLOR_TEXT, False),
            ("They will never know how close the mainframe was to doom.", COLOR_TEXT, False),
            ("", COLOR_TEXT, False),
            ("[ GRAVEYARD SHIFT PERFORMANCE REPORT ]", COLOR_TERMINAL_OFF, True),
            (f"  • Sectors Cleared       : 12 / 12  [100% ONLINE]", COLOR_EXIT_OPEN, False),
            (f"  • Total Moves Executed  : {moves}", COLOR_TEXT, False),
            (f"  • Dimensional Shifts    : {shifts}", COLOR_PLAYER, False),
            (f"  • Terminals Rebooted    : {reboots}", COLOR_TERMINAL_OFF, False),
            (f"  • Overtime Compensation : [DENIED - HR Policy §4.2]", (245, 90, 90), False),
            (f"  • Shift Performance     : S-RANK (Operator of the Month)", COLOR_EXIT_OPEN, True),
            ("", COLOR_TEXT, False),
            ("Time to punch out, Operator. You survived the night shift.", (220, 230, 245), False),
        ]

        # Teletype animation progression
        self.current_line_idx = 0
        self.current_char_idx = 0
        self.tick_counter = 0
        self.ticks_per_char = 1
        self.is_finished = False

        # Visual blink counters
        self.cursor_blink = 0
        self.prompt_blink = 0

        # Victory fanfare & restore music
        self.game.audio.set_dimension_music(False)
        self.game.audio.play_victory_fanfare()

    def handle_events(self, events: list[pygame.event.Event], actions: list[Action]):
        for action in actions:
            if action == Action.CONFIRM:
                if not self.is_finished:
                    # Fast-forward typing
                    self.current_line_idx = len(self.script_data)
                    self.current_char_idx = 0
                    self.is_finished = True
                else:
                    # Return to title screen
                    self._return_to_title()
                return

            elif action in (Action.CANCEL, Action.PAUSE):
                self._return_to_title()
                return

    def _return_to_title(self):
        """Transitions back to the main title screen."""
        from src.scenes.title_scene import TitleScene

        self.game.change_scene(TitleScene(self.game))

    def update(self):
        self.cursor_blink = (self.cursor_blink + 1) % 30
        self.prompt_blink = (self.prompt_blink + 1) % 40

        if not self.is_finished:
            self.tick_counter += 1
            if self.tick_counter >= self.ticks_per_char:
                self.tick_counter = 0
                self._advance_teletype()

    def _advance_teletype(self):
        """Reveals text letter-by-letter with subtle keyboard clicks."""
        if self.current_line_idx >= len(self.script_data):
            self.is_finished = True
            return

        text, _, _ = self.script_data[self.current_line_idx]

        if self.current_char_idx < len(text):
            char = text[self.current_char_idx]
            self.current_char_idx += 1
            if char.strip() and (self.current_char_idx % 2 == 0):
                self.game.audio.play_key_click()
        else:
            self.current_line_idx += 1
            self.current_char_idx = 0
            if self.current_line_idx >= len(self.script_data):
                self.is_finished = True

    def draw(self, screen: pygame.Surface):
        # Slate terminal background
        screen.fill(COLOR_BG_NORMAL)

        # Terminal outer frame / bezel
        bezel_rect = pygame.Rect(20, 20, SCREEN_WIDTH - 40, SCREEN_HEIGHT - 40)
        pygame.draw.rect(screen, (35, 45, 60), bezel_rect, width=2, border_radius=6)

        # Header tag
        pygame.draw.line(screen, (35, 45, 60), (20, 52), (SCREEN_WIDTH - 20, 52), width=1)
        header_tag = self.font.render(
            " OMNICORP HR TERMINAL // SHIFT END LOG // PORT 443 ", True, (90, 110, 140)
        )
        screen.blit(header_tag, (35, 30))

        # Render typed script lines
        start_x = 42
        start_y = 66
        line_height = 22

        for i, (full_text, color, is_bold) in enumerate(self.script_data):
            y = start_y + (i * line_height)

            if i < self.current_line_idx:
                font = self.font_bold if is_bold else self.font
                surf = font.render(full_text, True, color)
                screen.blit(surf, (start_x, y))

            elif i == self.current_line_idx and not self.is_finished:
                visible_text = full_text[: self.current_char_idx]
                font = self.font_bold if is_bold else self.font
                surf = font.render(visible_text, True, color)
                screen.blit(surf, (start_x, y))

                # Blinking cursor block
                cursor_x = start_x + surf.get_width() + 2
                if self.cursor_blink < 18:
                    pygame.draw.rect(screen, color, (cursor_x, y + 2, 8, 14))
                break

        # Bottom prompt
        if self.is_finished:
            if self.prompt_blink < 25:
                prompt_surf = self.prompt_font.render(
                    "[ PRESS ENTER / SPACE TO CLOCK OUT & EXIT ]", True, COLOR_EXIT_OPEN
                )
                screen.blit(
                    prompt_surf,
                    (SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2, SCREEN_HEIGHT - 65),
                )
        else:
            skip_hint = self.font.render(
                "[SPACE / ENTER]: Fast-Forward   |   [ESC]: Skip Outro",
                True,
                (100, 120, 145),
            )
            screen.blit(
                skip_hint,
                (SCREEN_WIDTH // 2 - skip_hint.get_width() // 2, SCREEN_HEIGHT - 62),
            )
