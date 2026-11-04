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


# Story & Lore Briefing Script
BRIEFING_DATA: list[tuple[str, tuple[int, int, int]]] = [
    (">>> OMNICORP MAINFRAME TERMINAL v4.2.0 <<<", COLOR_PLAYER),
    ("INCIDENT ID : #9904-QUANTUM-LEAK", COLOR_TERMINAL_OFF),
    ("TIMESTAMP   : 03:14:07 AM (GRAVEYARD SHIFT)", COLOR_TEXT_DIM),
    ("", COLOR_TEXT),
    ("URGENT MEMO: TO JUNIOR OPERATOR ON DUTY", (240, 240, 250)),
    ("--------------------------------------------------", (65, 80, 105)),
    ("At 03:00, a memory corruption breached reality bounds.", COLOR_TEXT),
    ("The mainframe has split into NORMAL and CORRUPTED layers.", COLOR_TEXT),
    ("Senior sysadmins are unreachable. The core is failing.", COLOR_TEXT),
    ("", COLOR_TEXT),
    ("SYSTEM PROTOCOLS & DIRECTIVES:", COLOR_EXIT_OPEN),
    (" 1. PHASE REALITY  : [SPACE / SHIFT] to bypass obstacles.", COLOR_TEXT),
    (" 2. REBOOT SERVERS : Access amber terminals to unlock doors.", COLOR_TEXT),
    (" 3. PUSH RAM       : Move quantum blocks onto pressure plates.", COLOR_TEXT),
    (" 4. AVOID SENTINELS: Corrupted daemons patrol the deep core.", COLOR_TEXT),
    ("", COLOR_TEXT),
    ("Restore all 12 sectors before daybreak. Do not crash.", COLOR_TERMINAL_OFF),
]


class IntroScene(Scene):
    """
    Narrative introduction briefing presented as a vintage CRT terminal teletype.
    Introduces the story lore, instructions, and objectives step-by-step.
    """

    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("monospace", 15)
        self.font_bold = pygame.font.SysFont("monospace", 15, bold=True)
        self.prompt_font = pygame.font.SysFont("monospace", 16, bold=True)

        # Teletype progression tracking
        self.current_line_idx = 0
        self.current_char_idx = 0
        self.tick_counter = 0
        self.ticks_per_char = 1  # 60 chars per second for snappy typing
        self.is_finished = False

        # Visual blink effects
        self.cursor_blink = 0
        self.prompt_blink = 0

    def handle_events(self, events: list[pygame.event.Event], actions: list[Action]):
        for action in actions:
            if action == Action.CONFIRM:
                if not self.is_finished:
                    # Fast-forward: reveal entire briefing immediately
                    self.current_line_idx = len(BRIEFING_DATA)
                    self.current_char_idx = 0
                    self.is_finished = True
                else:
                    # Proceed to first level
                    self._start_game()
                return

            elif action in (Action.CANCEL, Action.PAUSE):
                # Skip intro directly
                self._start_game()
                return

    def _start_game(self):
        """Transitions into gameplay at Sector 1, Level 0."""
        from src.scenes.game_scene import GameScene

        self.game.change_scene(GameScene(self.game, level_index=0))

    def update(self):
        self.cursor_blink = (self.cursor_blink + 1) % 30
        self.prompt_blink = (self.prompt_blink + 1) % 40

        if not self.is_finished:
            self.tick_counter += 1
            if self.tick_counter >= self.ticks_per_char:
                self.tick_counter = 0
                self._advance_teletype()

    def _advance_teletype(self):
        """Advances typing by one character and plays a subtle key click sound."""
        if self.current_line_idx >= len(BRIEFING_DATA):
            self.is_finished = True
            return

        text, _ = BRIEFING_DATA[self.current_line_idx]

        if self.current_char_idx < len(text):
            char = text[self.current_char_idx]
            self.current_char_idx += 1
            # Play mechanical click for non-space characters (every 2nd char for smooth cadence)
            if char.strip() and (self.current_char_idx % 2 == 0):
                self.game.audio.play_key_click()
        else:
            # Move to next line
            self.current_line_idx += 1
            self.current_char_idx = 0
            if self.current_line_idx >= len(BRIEFING_DATA):
                self.is_finished = True

    def draw(self, screen: pygame.Surface):
        # Clear background with dark terminal tone
        screen.fill(COLOR_BG_NORMAL)

        # Draw terminal frame / bezel
        bezel_rect = pygame.Rect(20, 20, SCREEN_WIDTH - 40, SCREEN_HEIGHT - 40)
        pygame.draw.rect(screen, (35, 45, 60), bezel_rect, width=2, border_radius=6)

        # Draw terminal header line
        pygame.draw.line(screen, (35, 45, 60), (20, 52), (SCREEN_WIDTH - 20, 52), width=1)
        header_tag = self.font.render(" OMNICORP SECURE TTY // TTY-7 // PORT 22 ", True, (90, 110, 140))
        screen.blit(header_tag, (35, 30))

        # Render typed briefing lines
        start_x = 42
        start_y = 68
        line_height = 23

        for i, (full_text, color) in enumerate(BRIEFING_DATA):
            y = start_y + (i * line_height)

            if i < self.current_line_idx:
                # Fully revealed line
                use_font = self.font_bold if i in (0, 1, 4, 10) else self.font
                surf = use_font.render(full_text, True, color)
                screen.blit(surf, (start_x, y))

            elif i == self.current_line_idx and not self.is_finished:
                # Currently typing line
                visible_text = full_text[: self.current_char_idx]
                use_font = self.font_bold if i in (0, 1, 4, 10) else self.font
                surf = use_font.render(visible_text, True, color)
                screen.blit(surf, (start_x, y))

                # Blinking terminal block cursor
                cursor_x = start_x + surf.get_width() + 2
                if self.cursor_blink < 18:
                    pygame.draw.rect(screen, color, (cursor_x, y + 2, 8, 14))
                break

        # Bottom control bar
        if self.is_finished:
            # Pulsing start prompt
            if self.prompt_blink < 25:
                prompt_surf = self.prompt_font.render(
                    "[ PRESS ENTER / SPACE TO COMMENCE SHIFT ]", True, COLOR_EXIT_OPEN
                )
                screen.blit(
                    prompt_surf,
                    (SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2, SCREEN_HEIGHT - 65),
                )
        else:
            skip_hint = self.font.render(
                "[SPACE / ENTER]: Fast-Forward   |   [ESC]: Skip Briefing",
                True,
                (100, 120, 145),
            )
            screen.blit(
                skip_hint,
                (SCREEN_WIDTH // 2 - skip_hint.get_width() // 2, SCREEN_HEIGHT - 62),
            )
