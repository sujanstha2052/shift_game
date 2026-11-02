from enum import Enum, auto
import pygame


class Action(Enum):
    """
    Game Actions represent player intent, completely decoupled
    from whether they are using a keyboard, mouse, or gamepad.
    """
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    SHIFT = auto()
    RESTART = auto()
    UNDO = auto()
    PAUSE = auto()
    CONFIRM = auto()
    CANCEL = auto()


class InputHandler:
    """
    Translates raw Pygame keyboard and joystick/gamepad events into Actions.
    """

    def __init__(self):
        # 1. Initialize Pygame joystick subsystem
        pygame.joystick.init()
        self.joysticks: list[pygame.joystick.JoystickType] = []
        self._init_joysticks()

        # Analog stick deadzone (to ignore tiny stick drifts)
        self.stick_deadzone = 0.5
        self.stick_moved_x = False
        self.stick_moved_y = False

        # 2. Keyboard Key Mappings (can easily be customized later)
        self.key_map = {
            # Movement
            pygame.K_UP: Action.UP,
            pygame.K_w: Action.UP,
            pygame.K_DOWN: Action.DOWN,
            pygame.K_s: Action.DOWN,
            pygame.K_LEFT: Action.LEFT,
            pygame.K_a: Action.LEFT,
            pygame.K_RIGHT: Action.RIGHT,
            pygame.K_d: Action.RIGHT,
            # Core Game Mechanics
            pygame.K_LSHIFT: Action.SHIFT,
            pygame.K_RSHIFT: Action.SHIFT,
            pygame.K_SPACE: Action.SHIFT,
            # QoL Controls
            pygame.K_r: Action.RESTART,
            pygame.K_z: Action.UNDO,
            pygame.K_u: Action.UNDO,
            # Menu & Navigation
            pygame.K_ESCAPE: Action.PAUSE,
            pygame.K_RETURN: Action.CONFIRM,
            pygame.K_KP_ENTER: Action.CONFIRM,
            pygame.K_q: Action.CANCEL,
        }

        # 3. Gamepad Button Mappings (Standard Xbox / PlayStation layout)
        # Button 0: A (Xbox) / Cross (PS)
        # Button 1: B (Xbox) / Circle (PS)
        # Button 2: X (Xbox) / Square (PS)
        # Button 3: Y (Xbox) / Triangle (PS)
        # Button 4/5: Shoulder Bumpers (LB / RB)
        # Button 6: Back / Select / Share
        # Button 7: Start / Options
        self.button_map = {
            0: Action.CONFIRM,   # A button -> Confirm / Select
            1: Action.CANCEL,    # B button -> Cancel / Back
            2: Action.RESTART,   # X button -> Quick Restart
            3: Action.UNDO,      # Y button -> Undo step
            4: Action.SHIFT,     # Left Bumper -> Dimension Shift
            5: Action.SHIFT,     # Right Bumper -> Dimension Shift
            7: Action.PAUSE,     # Start / Options -> Pause
        }

    def _init_joysticks(self):
        """Detect and initialize all currently connected controllers."""
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            self.joysticks.append(joy)

    def process_events(self, events: list[pygame.event.Event]) -> list[Action]:
        """
        Takes the raw Pygame events from the frame and returns a list of
        high-level Actions that occurred this frame.
        """
        actions: list[Action] = []

        for event in events:
            # 1. Hotplugging: Controller connected or disconnected
            if event.type == pygame.JOYDEVICEADDED or event.type == pygame.JOYDEVICEREMOVED:
                self._init_joysticks()

            # 2. Keyboard Key Pressed
            elif event.type == pygame.KEYDOWN:
                if event.key in self.key_map:
                    actions.append(self.key_map[event.key])

            # 3. Gamepad Button Pressed
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button in self.button_map:
                    actions.append(self.button_map[event.button])

            # 4. Gamepad D-Pad (Hat motion: returns tuple of (x, y))
            elif event.type == pygame.JOYHATMOTION:
                hat_x, hat_y = event.value
                if hat_x == 1:
                    actions.append(Action.RIGHT)
                elif hat_x == -1:
                    actions.append(Action.LEFT)
                if hat_y == 1:
                    actions.append(Action.UP)
                elif hat_y == -1:
                    actions.append(Action.DOWN)

            # 5. Gamepad Left Analog Stick (Axis 0 = X, Axis 1 = Y)
            elif event.type == pygame.JOYAXISMOTION:
                if event.axis == 0:  # Horizontal
                    if event.value > self.stick_deadzone and not self.stick_moved_x:
                        actions.append(Action.RIGHT)
                        self.stick_moved_x = True
                    elif event.value < -self.stick_deadzone and not self.stick_moved_x:
                        actions.append(Action.LEFT)
                        self.stick_moved_x = True
                    elif abs(event.value) < 0.2:
                        self.stick_moved_x = False  # Reset stick center

                elif event.axis == 1:  # Vertical
                    if event.value > self.stick_deadzone and not self.stick_moved_y:
                        actions.append(Action.DOWN)
                        self.stick_moved_y = True
                    elif event.value < -self.stick_deadzone and not self.stick_moved_y:
                        actions.append(Action.UP)
                        self.stick_moved_y = True
                    elif abs(event.value) < 0.2:
                        self.stick_moved_y = False  # Reset stick center

        return actions
