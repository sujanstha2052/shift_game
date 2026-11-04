import sys
import pygame
from src.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    TITLE,
)
from src.scenes import Scene, TitleScene
from src.input_handler import InputHandler
from src.audio import AudioManager


class Game:
    """
    Main Game application.
    Manages display, clock, input translation, audio, and scene stack.
    """

    def __init__(self):
        # 1. Initialize Pygame
        pygame.init()
        pygame.font.init()

        # 2. Window setup
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # 3. Audio & Input subsystems
        self.audio = AudioManager()
        self.input = InputHandler()

        # 4. Session Statistics (Tracks overall graveyard shift performance)
        self.stats = {"moves": 0, "shifts": 0, "reboots": 0}

        # 5. Visual Shaders & CRT Filter Overlay
        from src.crt_filter import create_crt_overlay
        self.crt_filter_enabled: bool = True
        self.crt_overlay: pygame.Surface | None = create_crt_overlay(SCREEN_WIDTH, SCREEN_HEIGHT)

        # 6. Scene Stack: Starts on the Title Screen
        self.scene_stack: list[Scene] = [TitleScene(self)]

    @property
    def current_scene(self) -> Scene:
        """Returns the scene currently at the top of the stack."""
        return self.scene_stack[-1]

    def change_scene(self, scene: Scene):
        """Replaces the entire stack with a new scene (e.g. Title -> Game)."""
        self.scene_stack = [scene]

    def push_scene(self, scene: Scene):
        """Pushes an overlay scene on top of the current one (e.g. Pause over Game)."""
        self.scene_stack.append(scene)

    def pop_scene(self):
        """Removes the top scene and returns to the previous one (e.g. Unpausing)."""
        if len(self.scene_stack) > 1:
            self.scene_stack.pop()

    def handle_events(self):
        """Collects events, translates them into actions, and passes them to the active scene."""
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return

        # Translate raw events into player actions (Action.UP, Action.SHIFT, etc.)
        actions = self.input.process_events(events)

        # Delegate to the active scene
        self.current_scene.handle_events(events, actions)

    def toggle_crt_filter(self):
        """Toggles the retro CRT scanline & vignette shader on or off."""
        self.crt_filter_enabled = not self.crt_filter_enabled

    def update(self):
        """Updates the active scene."""
        self.current_scene.update()

    def draw(self):
        """Draws the active scene, blits CRT scanlines if enabled, and flips display."""
        self.current_scene.draw(self.screen)
        if self.crt_filter_enabled and self.crt_overlay:
            self.screen.blit(self.crt_overlay, (0, 0))
        pygame.display.flip()

    def run(self):
        """The master 60 FPS loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        # Cleanup on exit
        pygame.quit()
        sys.exit()
