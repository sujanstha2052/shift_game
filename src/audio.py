import math
import struct
import pygame


class AudioManager:
    """
    Synthesizes and plays procedural retro 8-bit sound effects and
    interactive dual-layer ambient synth music in memory.
    Zero external audio files required!
    """

    def __init__(self):
        self.enabled = False
        self.channel_bgm_norm = None
        self.channel_bgm_corr = None

        try:
            # Initialize Pygame mixer (44.1kHz, 16-bit signed, mono, 512 buffer for low latency)
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

            # Allocate 8 audio channels
            pygame.mixer.set_num_channels(8)
            # Channel 0 & 1 are dedicated to synchronized BGM layering
            self.channel_bgm_norm = pygame.mixer.Channel(0)
            self.channel_bgm_corr = pygame.mixer.Channel(1)

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
        self.push_sound = self._create_block_push_sound() if self.enabled else None
        self.switch_sound = self._create_switch_click_sound() if self.enabled else None
        self.daemon_step_sound = self._create_daemon_step_sound() if self.enabled else None
        self.alarm_sound = self._create_alarm_sound() if self.enabled else None
        self.fanfare_sound = self._create_victory_fanfare() if self.enabled else None
        self.key_click_sound = self._create_key_click_sound() if self.enabled else None

        # Generate synchronized background music loops
        if self.enabled:
            self.bgm_normal, self.bgm_corrupt = self._create_dual_bgm_loops()
        else:
            self.bgm_normal, self.bgm_corrupt = None, None

    # =========================================================================
    # SFX SYNTHESIS
    # =========================================================================
    def _create_bump_sound(self) -> pygame.mixer.Sound | None:
        try:
            sample_rate = 44100
            duration = 0.06
            total_samples = int(sample_rate * duration)
            raw = bytearray()
            for i in range(total_samples):
                t = i / sample_rate
                prog = i / total_samples
                freq = 150.0 - (100.0 * prog)
                volume = (1.0 - prog) ** 1.5
                val = int(32767 * 0.35 * volume * math.sin(2.0 * math.pi * freq * t))
                raw.extend(struct.pack("<h", val))
            return pygame.mixer.Sound(buffer=bytes(raw))
        except Exception:
            return None

    def _create_undo_sound(self) -> pygame.mixer.Sound | None:
        try:
            sample_rate = 44100
            duration = 0.07
            total_samples = int(sample_rate * duration)
            raw = bytearray()
            for i in range(total_samples):
                t = i / sample_rate
                prog = i / total_samples
                freq = 250.0 + (250.0 * prog)
                volume = math.sin(math.pi * prog)
                val = int(32767 * 0.30 * volume * math.sin(2.0 * math.pi * freq * t))
                raw.extend(struct.pack("<h", val))
            return pygame.mixer.Sound(buffer=bytes(raw))
        except Exception:
            return None

    def _create_error_buzz_sound(self) -> pygame.mixer.Sound | None:
        try:
            sample_rate = 44100
            duration = 0.12
            total_samples = int(sample_rate * duration)
            raw = bytearray()
            for i in range(total_samples):
                t = i / sample_rate
                prog = i / total_samples
                burst = 1.0 if (int(t * 30) % 2 == 0) else 0.4
                volume = (1.0 - (prog * 0.5)) * burst
                sin_val = math.sin(2.0 * math.pi * 110.0 * t)
                wave = 1.0 if sin_val > 0 else -1.0
                val = int(32767 * 0.32 * volume * wave)
                raw.extend(struct.pack("<h", val))
            return pygame.mixer.Sound(buffer=bytes(raw))
        except Exception:
            return None

    def _create_shift_whoosh_sound(self) -> pygame.mixer.Sound | None:
        try:
            sample_rate = 44100
            duration = 0.18
            total_samples = int(sample_rate * duration)
            raw = bytearray()
            for i in range(total_samples):
                t = i / sample_rate
                prog = i / total_samples
                freq = 600.0 - (500.0 * (prog ** 0.5)) + (30.0 * math.sin(2.0 * math.pi * 35.0 * t))
                volume = math.sin(math.pi * prog)
                val = int(32767 * 0.35 * volume * math.sin(2.0 * math.pi * freq * t))
                raw.extend(struct.pack("<h", val))
            return pygame.mixer.Sound(buffer=bytes(raw))
        except Exception:
            return None

    def _create_reboot_sound(self) -> pygame.mixer.Sound | None:
        try:
            sample_rate = 44100
            duration = 0.20
            total_samples = int(sample_rate * duration)
            raw = bytearray()
            for i in range(total_samples):
                t = i / sample_rate
                freq = 440.0 if t < 0.08 else 880.0
                vol = math.exp(-t * 12.0) if t < 0.08 else math.exp(-(t - 0.08) * 8.0)
                val = int(32767 * 0.35 * vol * math.sin(2.0 * math.pi * freq * t))
                raw.extend(struct.pack("<h", val))
            return pygame.mixer.Sound(buffer=bytes(raw))
        except Exception:
            return None

    def _create_block_push_sound(self) -> pygame.mixer.Sound | None:
        try:
            sample_rate = 44100
            duration = 0.09
            total_samples = int(sample_rate * duration)
            raw = bytearray()
            for i in range(total_samples):
                t = i / sample_rate
                prog = i / total_samples
                freq = 180.0 - (120.0 * prog)
                vol = (1.0 - prog) ** 1.8
                tone = math.sin(2.0 * math.pi * freq * t) + (0.35 * math.sin(2.0 * math.pi * freq * 2.5 * t))
                val = int(32767 * 0.32 * vol * (tone / 1.35))
                raw.extend(struct.pack("<h", val))
            return pygame.mixer.Sound(buffer=bytes(raw))
        except Exception:
            return None

    def _create_switch_click_sound(self) -> pygame.mixer.Sound | None:
        try:
            sample_rate = 44100
            duration = 0.04
            total_samples = int(sample_rate * duration)
            raw = bytearray()
            for i in range(total_samples):
                t = i / sample_rate
                prog = i / total_samples
                freq = 900.0 - (400.0 * prog)
                vol = (1.0 - prog) ** 3.0
                val = int(32767 * 0.35 * vol * math.sin(2.0 * math.pi * freq * t))
                raw.extend(struct.pack("<h", val))
            return pygame.mixer.Sound(buffer=bytes(raw))
        except Exception:
            return None

    def _create_daemon_step_sound(self) -> pygame.mixer.Sound | None:
        try:
            sample_rate = 44100
            duration = 0.05
            total_samples = int(sample_rate * duration)
            raw = bytearray()
            for i in range(total_samples):
                t = i / sample_rate
                prog = i / total_samples
                freq = 300.0 - (150.0 * prog)
                vol = (1.0 - prog) ** 2.0
                val = int(32767 * 0.25 * vol * math.sin(2.0 * math.pi * freq * t))
                raw.extend(struct.pack("<h", val))
            return pygame.mixer.Sound(buffer=bytes(raw))
        except Exception:
            return None

    def _create_alarm_sound(self) -> pygame.mixer.Sound | None:
        try:
            sample_rate = 44100
            duration = 0.16
            total_samples = int(sample_rate * duration)
            raw = bytearray()
            for i in range(total_samples):
                t = i / sample_rate
                freq = 600.0 + 300.0 * math.sin(2.0 * math.pi * 15.0 * t)
                vol = math.sin(math.pi * (i / total_samples))
                val = int(32767 * 0.35 * vol * math.sin(2.0 * math.pi * freq * t))
                raw.extend(struct.pack("<h", val))
            return pygame.mixer.Sound(buffer=bytes(raw))
        except Exception:
            return None

    def _create_victory_fanfare(self) -> pygame.mixer.Sound | None:
        """Ascending C-E-G-C major chord arpeggio for sector clear."""
        try:
            sample_rate = 44100
            duration = 0.45
            total_samples = int(sample_rate * duration)
            raw = bytearray()
            notes = [523.25, 659.25, 783.99, 1046.50]
            for i in range(total_samples):
                t = i / sample_rate
                idx = min(3, int(t / 0.10))
                freq = notes[idx]
                env = math.exp(-(t % 0.10) * 10.0) if idx < 3 else math.exp(-(t - 0.30) * 4.0)
                val = int(32767 * 0.35 * env * math.sin(2.0 * math.pi * freq * t))
                raw.extend(struct.pack("<h", val))
            return pygame.mixer.Sound(buffer=bytes(raw))
        except Exception:
            return None

    def _create_key_click_sound(self) -> pygame.mixer.Sound | None:
        """Subtle mechanical terminal key click for teletype text."""
        try:
            sample_rate = 44100
            duration = 0.015
            total_samples = int(sample_rate * duration)
            raw = bytearray()
            for i in range(total_samples):
                t = i / sample_rate
                prog = i / total_samples
                freq = 1400.0 - (600.0 * prog)
                vol = (1.0 - prog) ** 2.0
                val = int(32767 * 0.12 * vol * math.sin(2.0 * math.pi * freq * t))
                raw.extend(struct.pack("<h", val))
            return pygame.mixer.Sound(buffer=bytes(raw))
        except Exception:
            return None

    # =========================================================================
    # DUAL-DIMENSION BGM GENERATION
    # =========================================================================
    def _create_dual_bgm_loops(self):
        """
        Synthesizes a 4.36-second seamless synthwave loop (110 BPM, 8 beats).
        Generates two synchronized layers: Normal (clean tech) and Corrupt (glitch saw).
        """
        try:
            sample_rate = 44100
            bpm = 110
            beat_len = 60.0 / bpm
            beats = 8
            duration = beats * beat_len
            total_samples = int(sample_rate * duration)

            raw_normal = bytearray()
            raw_corrupt = bytearray()
            bass_notes = [55.0, 55.0, 65.4, 65.4, 73.4, 73.4, 82.4, 55.0]

            for i in range(total_samples):
                t = i / sample_rate
                beat_idx = int(t / beat_len) % beats
                beat_time = t % beat_len

                # 1. Sub Bassline
                bass_freq = bass_notes[beat_idx]
                bass_env = math.exp(-beat_time * 4.0)
                bass_val = math.sin(2.0 * math.pi * bass_freq * t) * bass_env

                # 2. Cyber Arpeggio (440, 659, 523, 880)
                arp_notes = [440.0, 659.25, 523.25, 880.0]
                arp_idx = int(beat_time * 8.0) % 4
                arp_freq = arp_notes[arp_idx]
                arp_env = math.exp(-(beat_time % 0.125) * 16.0)
                arp_val = math.sin(2.0 * math.pi * arp_freq * t) * arp_env * 0.25

                # Normal Layer Mix
                sample_norm = int(32767 * 0.35 * (bass_val + arp_val))
                raw_normal.extend(struct.pack("<h", max(-32767, min(32767, sample_norm))))

                # Corrupt Layer Mix (Sawtooth Bass + Glitch Static)
                saw_val = (2.0 * ((t * bass_freq) % 1.0) - 1.0) * bass_env
                glitch_noise = ((i * 1103515245 + 12345) & 0x7FFFFFFF) / 0x7FFFFFFF - 0.5
                sample_corr = int(32767 * 0.30 * (saw_val * 0.7 + glitch_noise * 0.12))
                raw_corrupt.extend(struct.pack("<h", max(-32767, min(32767, sample_corr))))

            snd_norm = pygame.mixer.Sound(buffer=bytes(raw_normal))
            snd_corr = pygame.mixer.Sound(buffer=bytes(raw_corrupt))
            return snd_norm, snd_corr
        except Exception as e:
            print(f"[Audio] Could not synthesize BGM: {e}")
            return None, None

    # =========================================================================
    # PLAYBACK CONTROL
    # =========================================================================
    def start_music(self):
        """Starts both synchronized BGM tracks looping indefinitely."""
        if not self.enabled or not self.bgm_normal or not self.bgm_corrupt:
            return
        if not self.channel_bgm_norm.get_busy():
            self.channel_bgm_norm.play(self.bgm_normal, loops=-1)
            self.channel_bgm_norm.set_volume(0.28)
        if not self.channel_bgm_corr.get_busy():
            self.channel_bgm_corr.play(self.bgm_corrupt, loops=-1)
            self.channel_bgm_corr.set_volume(0.0)

    def set_dimension_music(self, is_corrupted: bool):
        """Seamlessly crossfades between Normal and Corrupt music tracks in-beat!"""
        if not self.enabled:
            return
        if is_corrupted:
            if self.channel_bgm_norm:
                self.channel_bgm_norm.set_volume(0.0)
            if self.channel_bgm_corr:
                self.channel_bgm_corr.set_volume(0.25)
        else:
            if self.channel_bgm_norm:
                self.channel_bgm_norm.set_volume(0.28)
            if self.channel_bgm_corr:
                self.channel_bgm_corr.set_volume(0.0)

    def stop_music(self):
        """Stops both music channels."""
        if self.enabled:
            if self.channel_bgm_norm:
                self.channel_bgm_norm.stop()
            if self.channel_bgm_corr:
                self.channel_bgm_corr.stop()

    def play_bump(self):
        if self.enabled and self.bump_sound:
            self.bump_sound.play()

    def play_undo(self):
        if self.enabled and self.undo_sound:
            self.undo_sound.play()

    def play_error_buzz(self):
        if self.enabled and self.error_buzz_sound:
            self.error_buzz_sound.play()

    def play_shift_whoosh(self):
        if self.enabled and self.shift_whoosh_sound:
            self.shift_whoosh_sound.play()

    def play_reboot(self):
        if self.enabled and self.reboot_sound:
            self.reboot_sound.play()

    def play_block_push(self):
        if self.enabled and self.push_sound:
            self.push_sound.play()

    def play_switch_click(self):
        if self.enabled and self.switch_sound:
            self.switch_sound.play()

    def play_daemon_step(self):
        if self.enabled and self.daemon_step_sound:
            self.daemon_step_sound.play()

    def play_alarm(self):
        if self.enabled and self.alarm_sound:
            self.alarm_sound.play()

    def play_key_click(self):
        if self.enabled and self.key_click_sound:
            self.key_click_sound.play()

    def play_victory_fanfare(self):
        if self.enabled and self.fanfare_sound:
            self.fanfare_sound.play()
