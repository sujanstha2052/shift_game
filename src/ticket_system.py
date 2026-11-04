import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_TERMINAL_OFF,
    COLOR_TEXT,
)

# Curated catalog of humorous graveyard-shift IT support tickets & server logs
TICKETS: list[str] = [
    "Ticket #102: Printer in accounting is summoning demons again.",
    "Ticket #404: Who pushed directly to production on Friday evening?",
    "Ticket #089: User unplugged core switch to charge their vape.",
    "Ticket #256: Production database is running on a dusty Raspberry Pi 2.",
    "Ticket #301: Coffee machine IP conflicts with primary DNS gateway.",
    "Ticket #503: The sentient daemon in sector 3 requested dental benefits.",
    "Ticket #777: Security audit failed: root password was set to 'admin123'.",
    "Ticket #042: Quantum entanglement detected in server rack 4.",
    "Ticket #666: Sudo command responded: 'No, I don't think I will'.",
    "Ticket #133: Rack cooling fan sounds like an angry dial-up modem.",
    "Ticket #999: Git merge conflict caused a localized black hole in kernel.",
    "Ticket #808: Automated backup script was piping directly to /dev/null.",
    "Ticket #512: Automated test suite passed because assertions were deleted.",
    "Ticket #714: Floating point error caused office thermostat to freeze at -459°F.",
]


class TicketPopup:
    """
    Manages and renders humorous IT ticket notifications when terminals are rebooted.
    Handles timer countdown and smooth alpha fade-out.
    """

    def __init__(self):
        self.font_tag = pygame.font.SysFont("monospace", 12, bold=True)
        self.font_msg = pygame.font.SysFont("monospace", 13)

        self.active_ticket: str | None = None
        self.timer: int = 0
        self.max_duration: int = 200  # ~3.3 seconds at 60 FPS
        self.fade_duration: int = 30  # Last 0.5s for smooth fade out
        self._ticket_index: int = 0

    def trigger(self):
        """Fetches the next ticket from the pool and triggers the popup display."""
        self.active_ticket = TICKETS[self._ticket_index]
        self._ticket_index = (self._ticket_index + 1) % len(TICKETS)
        self.timer = self.max_duration

    def update(self):
        """Decrements display timer each game frame."""
        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                self.active_ticket = None

    def draw(self, screen: pygame.Surface):
        """Renders the toast notification at the bottom of the screen with smooth alpha fade."""
        if self.timer <= 0 or not self.active_ticket:
            return

        # Calculate fade alpha (255 during main show, decreasing during fade_duration)
        alpha = 255
        if self.timer < self.fade_duration:
            alpha = int(255 * (self.timer / self.fade_duration))

        # Box dimensions
        box_width = min(680, SCREEN_WIDTH - 48)
        box_height = 42
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = SCREEN_HEIGHT - 54

        # Create temporary surface supporting transparency
        toast_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)

        # 1. Background fill (dark translucent slate)
        bg_color = (18, 22, 32, int(220 * (alpha / 255.0)))
        toast_surf.fill(bg_color)

        # 2. Border glow (amber terminal accent)
        border_color = (*COLOR_TERMINAL_OFF, alpha)
        pygame.draw.rect(
            toast_surf,
            border_color,
            pygame.Rect(0, 0, box_width, box_height),
            width=2,
            border_radius=5,
        )

        # 3. Tag prefix (e.g. "[SYSADMIN TICKET]")
        tag_surf = self.font_tag.render("[SYSADMIN LOG]", True, COLOR_TERMINAL_OFF)
        tag_surf.set_alpha(alpha)
        toast_surf.blit(tag_surf, (12, 13))

        # 4. Ticket message text
        msg_surf = self.font_msg.render(self.active_ticket, True, COLOR_TEXT)
        msg_surf.set_alpha(alpha)
        toast_surf.blit(msg_surf, (140, 13))

        # Blit final toast onto game screen
        screen.blit(toast_surf, (box_x, box_y))
