from dataclasses import dataclass
import pygame
from src.input_handler import Action


@dataclass
class StateSnapshot:
    """A frozen snapshot of game state at a specific point in time for the Undo system."""
    player_x: int
    player_y: int
    facing_x: int
    facing_y: int
    is_corrupted: bool
    terminals_rebooted: tuple[bool, ...]
    blocks_state: tuple[tuple[int, int], ...]
    daemons_state: tuple[tuple[int, int, int, int], ...]


class Scene:
    """
    Base Scene class that all scenes inherit from.
    Provides standard lifecycle methods: handle_events, update, and draw.
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
