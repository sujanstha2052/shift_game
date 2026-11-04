# Screen & Grid Settings
TILE_SIZE = 48        # 48x48 pixels per tile
GRID_WIDTH = 16       # 16 tiles across
GRID_HEIGHT = 12      # 12 tiles down

SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH   # 768px
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT # 576px

FPS = 60
TITLE = "Shift/Return - Game Off 2026"

# Color Palette: Normal Dimension (Server Room)
COLOR_BG_NORMAL = (24, 28, 36)
COLOR_WALL_NORMAL = (65, 80, 105)
COLOR_WALL_BORDER_NORMAL = (90, 110, 145)

# Color Palette: Corrupted Dimension (System Glitch)
COLOR_BG_CORRUPT = (38, 14, 20)
COLOR_WALL_CORRUPT = (140, 42, 60)
COLOR_WALL_BORDER_CORRUPT = (185, 65, 88)

COLOR_GRID_LINE = (38, 42, 52)
COLOR_TEXT = (220, 225, 235)
COLOR_TEXT_DIM = (140, 155, 175)

# Entity Colors: Player
COLOR_PLAYER = (64, 165, 255)
COLOR_PLAYER_BORDER = (20, 90, 160)

# Interactive Objects: Terminals & Exit Gateway
COLOR_TERMINAL_OFF = (245, 166, 35)      # Amber glowing server (Needs reboot)
COLOR_TERMINAL_REBOOTED = (78, 201, 138) # Neon green (Rebooted)
COLOR_EXIT_LOCKED = (180, 60, 60)        # Red locked gateway
COLOR_EXIT_OPEN = (52, 211, 153)         # Green open gateway

# Interactive Objects: RAM Blocks
COLOR_RAM_QUANTUM_BG = (75, 45, 115)     # Deep indigo
COLOR_RAM_QUANTUM_BORDER = (245, 195, 65)# Gold
COLOR_RAM_NORMAL_BG = (45, 65, 90)       # Steel blue
COLOR_RAM_NORMAL_BORDER = (65, 160, 240) # Cyan
COLOR_RAM_CORRUPT_BG = (120, 25, 45)     # Crimson
COLOR_RAM_CORRUPT_BORDER = (255, 65, 115)# Hot pink

# Interactive Objects: Pressure Plates & Lasers
COLOR_PLATE_BASE = (40, 50, 70)
COLOR_PLATE_PRESSED = (52, 211, 153)
COLOR_PLATE_UNPRESSED = (120, 140, 170)
COLOR_LASER_CORRUPT = (255, 45, 85)
COLOR_LASER_NORMAL = (45, 175, 255)

# Interactive Objects: Daemons & Hazards
COLOR_DAEMON_ACTIVE = (165, 20, 55)
COLOR_DAEMON_BORDER = (255, 60, 110)
COLOR_DAEMON_DORMANT = (35, 45, 60)
COLOR_HAZARD_RED = (255, 60, 90)
