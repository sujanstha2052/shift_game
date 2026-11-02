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

# Entity Colors
COLOR_PLAYER = (64, 165, 255)
COLOR_PLAYER_BORDER = (20, 90, 160)

# Interactive Object Colors
COLOR_TERMINAL_OFF = (245, 166, 35)      # Amber glowing server (Needs reboot)
COLOR_TERMINAL_REBOOTED = (78, 201, 138) # Neon green (Rebooted)
COLOR_EXIT_LOCKED = (180, 60, 60)        # Red locked gateway
COLOR_EXIT_OPEN = (52, 211, 153)         # Green open gateway