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
        self.error_buzz_sound = self._create_error_buzz_sound() if self.enabled else None
        self.shift_whoosh_sound = self._create_shift_whoosh_sound() if self.enabled else None
        self.reboot_sound = self._create_reboot_sound() if self.enabled else None

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

    def _create_error_buzz_sound(self) -> pygame.mixer.Sound | None:
        """
        Synthesizes an authentic 8-bit digital warning buzzer (120ms square wave)
        for when a dimension shift is blocked by a wall.
        """
        try:
            sample_rate = 44100
            duration = 0.12  # 120 milliseconds
            total_samples = int(sample_rate * duration)
            raw_data = bytearray()

            for i in range(total_samples):
                t = i / sample_rate
                progress = i / total_samples

                # Two distinct stutter pulses for computer warning feel
                burst = 1.0 if (int(t * 30) % 2 == 0) else 0.4
                volume = (1.0 - (progress * 0.5)) * burst

                # 110 Hz square wave (harsh digital buzz)
                sin_val = math.sin(2.0 * math.pi * 110.0 * t)
                wave = 1.0 if sin_val > 0 else -1.0

                sample_val = int(32767 * 0.32 * volume * wave)
                raw_data.extend(struct.pack("<h", sample_val))

            return pygame.mixer.Sound(buffer=bytes(raw_data))
        except Exception as e:
            print(f"[Audio] Could not synthesize error buzz: {e}")
            return None

    def _create_shift_whoosh_sound(self) -> pygame.mixer.Sound | None:
        """
        Synthesizes a resonant sci-fi pitch sweep (180ms, 600Hz -> 100Hz)
        with frequency modulation when successfully phasing dimensions.
        """
        try:
            sample_rate = 44100
            duration = 0.18  # 180 milliseconds
            total_samples = int(sample_rate * duration)
            raw_data = bytearray()

            for i in range(total_samples):
                t = i / sample_rate
                progress = i / total_samples

                # Frequency sweep with a subtle 35Hz vibrato warble
                freq = 600.0 - (500.0 * (progress ** 0.5)) + (30.0 * math.sin(2.0 * math.pi * 35.0 * t))
                volume = math.sin(math.pi * progress)

                sample_val = int(32767 * 0.35 * volume * math.sin(2.0 * math.pi * freq * t))
                raw_data.extend(struct.pack("<h", sample_val))

            return pygame.mixer.Sound(buffer=bytes(raw_data))
        except Exception as e:
            print(f"[Audio] Could not synthesize shift whoosh: {e}")
            return None

    def _create_reboot_sound(self) -> pygame.mixer.Sound | None:
        """
        Synthesizes a 2-tone melodic startup chime (200ms: 440Hz -> 880Hz)
        when rebooting an offline server terminal.
        """
        try:
            sample_rate = 44100
            duration = 0.20  # 200 milliseconds
            total_samples = int(sample_rate * duration)
            raw_data = bytearray()

            for i in range(total_samples):
                t = i / sample_rate
                # Note 1 (A4: 440Hz) for first 80ms, then Note 2 (A5: 880Hz) for remainder
                freq = 440.0 if t < 0.08 else 880.0
                vol = math.exp(-t * 12.0) if t < 0.08 else math.exp(-(t - 0.08) * 8.0)

                sample_val = int(32767 * 0.35 * vol * math.sin(2.0 * math.pi * freq * t))
                raw_data.extend(struct.pack("<h", sample_val))

            return pygame.mixer.Sound(buffer=bytes(raw_data))
        except Exception as e:
            print(f"[Audio] Could not synthesize reboot chime: {e}")
            return None

    def play_bump(self):
        """Plays the wall bump thud."""
        if self.enabled and self.bump_sound:
            self.bump_sound.play()

    def play_undo(self):
        """Plays the rewind blip."""
        if self.enabled and self.undo_sound:
            self.undo_sound.play()

    def play_error_buzz(self):
        """Plays the digital rejection buzzer."""
        if self.enabled and self.error_buzz_sound:
            self.error_buzz_sound.play()

    def play_shift_whoosh(self):
        """Plays the dimension shift whoosh."""
        if self.enabled and self.shift_whoosh_sound:
            self.shift_whoosh_sound.play()

    def play_reboot(self):
        """Plays the server terminal reboot chime."""
        if self.enabled and self.reboot_sound:
            self.reboot_sound.play()
