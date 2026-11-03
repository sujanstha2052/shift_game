import math
import struct
import pygame


class AudioManager:
    """
    Synthesizes and plays procedural retro 8-bit sound effects in memory.
    Zero external audio files required!
    """

    def __init__(self):
        self.enabled = False
        try:
            # Initialize Pygame mixer (44.1kHz, 16-bit signed, mono)
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.enabled = True
        except Exception as e:
            print(f"[Audio] Mixer could not be initialized: {e}")
            self.enabled = False

        # Generate sound effects in memory
        self.bump_sound = self._create_bump_sound() if self.enabled else None
        self.undo_sound = self._create_undo_sound() if self.enabled else None

    def _create_bump_sound(self) -> pygame.mixer.Sound | None:
        """
        Synthesizes a short, satisfying low-frequency thud (60ms)
        for when the player bumps into a wall.
        """
        try:
            sample_rate = 44100
            duration = 0.06  # 60 milliseconds
            total_samples = int(sample_rate * duration)
            raw_data = bytearray()

            for i in range(total_samples):
                t = i / sample_rate
                progress = i / total_samples

                # Frequency drops from 150 Hz down to 50 Hz (classic pitch drop thump)
                freq = 150.0 - (100.0 * progress)

                # Volume envelope: starts strong and quickly decays
                volume = (1.0 - progress) ** 1.5

                # Calculate sine wave value
                sample_val = int(32767 * 0.35 * volume * math.sin(2.0 * math.pi * freq * t))

                # Pack as 16-bit signed little-endian integer
                raw_data.extend(struct.pack("<h", sample_val))

            return pygame.mixer.Sound(buffer=bytes(raw_data))
        except Exception as e:
            print(f"[Audio] Could not synthesize bump sound: {e}")
            return None

    def _create_undo_sound(self) -> pygame.mixer.Sound | None:
        """
        Synthesizes a quick rising rewind blip (70ms, 250Hz -> 500Hz)
        when stepping backward in time.
        """
        try:
            sample_rate = 44100
            duration = 0.07  # 70 milliseconds
            total_samples = int(sample_rate * duration)
            raw_data = bytearray()

            for i in range(total_samples):
                t = i / sample_rate
                progress = i / total_samples

                # Frequency sweeps upward (giving a "rewind" sensation)
                freq = 250.0 + (250.0 * progress)

                # Smooth bell-shaped volume curve
                volume = math.sin(math.pi * progress)

                sample_val = int(32767 * 0.30 * volume * math.sin(2.0 * math.pi * freq * t))
                raw_data.extend(struct.pack("<h", sample_val))

            return pygame.mixer.Sound(buffer=bytes(raw_data))
        except Exception as e:
            print(f"[Audio] Could not synthesize undo sound: {e}")
            return None

    def play_bump(self):
        """Plays the wall bump thud."""
        if self.enabled and self.bump_sound:
            self.bump_sound.play()

    def play_undo(self):
        """Plays the rewind blip."""
        if self.enabled and self.undo_sound:
            self.undo_sound.play()
