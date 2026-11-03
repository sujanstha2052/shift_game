import pygame
from src.config import (
    TILE_SIZE,
    GRID_WIDTH,
    GRID_HEIGHT,
    COLOR_BG_NORMAL,
    COLOR_WALL_NORMAL,
    COLOR_WALL_BORDER_NORMAL,
    COLOR_BG_CORRUPT,
    COLOR_WALL_CORRUPT,
    COLOR_WALL_BORDER_CORRUPT,
)
from src.interactables import (
    Terminal,
    ExitDoor,
    RAMBlock,
    PressurePlate,
    LaserBarrier,
    DaemonSentinel,
)
from src.levels_data import LEVELS


class Level:
    def __init__(self, level_index: int = 0):
        self.level_index = level_index
        self.load_level(level_index)

    def load_level(self, index: int):
        """Loads a specific level configuration by its index."""
        data = LEVELS[index]
        self.id = data["id"]
        self.name = data["name"]
        self.player_start = data["player_start"]
        self.normal_map = data["normal_map"]
        self.corrupt_map = data["corrupt_map"]

        # Reset state flags
        self.is_corrupted = False
        self.is_won = False

        # 1. Terminals
        self.terminals = [
            Terminal(t["x"], t["y"], required_in_corrupt=t["corrupted"])
            for t in data["terminals"]
        ]

        # 2. RAM Blocks (optional per level)
        self.blocks = [
            RAMBlock(b["x"], b["y"], dimension=b.get("dimension", "both"))
            for b in data.get("blocks", [])
        ]

        # 3. Data Pressure Plates (optional per level)
        self.plates = [
            PressurePlate(
                p["x"],
                p["y"],
                channel=p.get("channel", "A"),
                dimension=p.get("dimension", "both"),
            )
            for p in data.get("plates", [])
        ]

        # 4. Firewalls / Laser Barriers (optional per level)
        self.lasers = [
            LaserBarrier(
                l["x"],
                l["y"],
                channel=l.get("channel", "A"),
                dimension=l.get("dimension", "corrupt"),
                orientation=l.get("orientation", "horizontal"),
            )
            for l in data.get("lasers", [])
        ]

        # 5. Corrupted Daemons / Sentinels (optional per level)
        self.daemons = [
            DaemonSentinel(
                d["patrol_points"],
                loop=d.get("loop", False),
            )
            for d in data.get("daemons", [])
        ]

        # 6. Exit Door
        exit_x, exit_y = data["exit_pos"]
        self.exit_door = ExitDoor(exit_x, exit_y)

    @property
    def current_map(self) -> list[list[int]]:
        return self.corrupt_map if self.is_corrupted else self.normal_map

    @property
    def all_terminals_rebooted(self) -> bool:
        return all(t.rebooted for t in self.terminals)

    @property
    def active_channels(self) -> set[str]:
        """Set of channels currently powered by active pressed pressure plates."""
        return {p.channel for p in self.plates if p.is_pressed}

    def is_wall(self, grid_x: int, grid_y: int) -> bool:
        """Returns True if the grid coordinate is out of bounds or a solid wall tile."""
        if not (0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT):
            return True
        return self.current_map[grid_y][grid_x] == 1

    def get_block_at(self, grid_x: int, grid_y: int) -> RAMBlock | None:
        """Returns the active RAM block at (grid_x, grid_y) if one exists."""
        for block in self.blocks:
            if block.is_active(self.is_corrupted) and block.grid_x == grid_x and block.grid_y == grid_y:
                return block
        return None

    def is_laser_active_at(self, grid_x: int, grid_y: int, is_corrupted: bool | None = None) -> bool:
        """Returns True if an energized laser beam is active at (grid_x, grid_y)."""
        corrupted = self.is_corrupted if is_corrupted is None else is_corrupted
        channels = self.active_channels

        for laser in self.lasers:
            if laser.grid_x == grid_x and laser.grid_y == grid_y:
                if laser.is_active(corrupted, channels):
                    for b in self.blocks:
                        if b.is_active(corrupted) and b.grid_x == grid_x and b.grid_y == grid_y:
                            return False  # Block shields the beam!
                    return True
        return False

    def is_daemon_at(self, grid_x: int, grid_y: int) -> bool:
        """Returns True if an active hostile daemon is at (grid_x, grid_y)."""
        if not self.is_corrupted:
            return False
        for d in self.daemons:
            if d.grid_x == grid_x and d.grid_y == grid_y:
                return True
        return False

    def is_solid(self, grid_x: int, grid_y: int) -> bool:
        """True if blocked by a wall, an active RAM block, or a lethal active laser."""
        if self.is_wall(grid_x, grid_y):
            return True
        if self.get_block_at(grid_x, grid_y) is not None:
            return True
        if self.is_laser_active_at(grid_x, grid_y):
            return True
        return False

    def step_daemons(self) -> bool:
        """Advances daemons along their patrol routes if active in Corrupted Dimension."""
        if not self.is_corrupted or not self.daemons:
            return False
        for d in self.daemons:
            d.step_patrol()
        return True

    def try_push_block(self, block: RAMBlock, dx: int, dy: int) -> bool:
        """Attempts to push a block in direction (dx, dy)."""
        dest_x = block.grid_x + dx
        dest_y = block.grid_y + dy

        if self.is_wall(dest_x, dest_y):
            return False

        for other in self.blocks:
            if other is not block and other.is_active(self.is_corrupted):
                if other.grid_x == dest_x and other.grid_y == dest_y:
                    return False

        block.push(dx, dy)
        return True

    def can_shift(self, player_x: int, player_y: int) -> bool:
        """Cannot shift into a wall, an active block, or an active laser."""
        target_corrupted = not self.is_corrupted
        target_map = self.normal_map if self.is_corrupted else self.corrupt_map

        if target_map[player_y][player_x] == 1:
            return False

        for block in self.blocks:
            if block.is_active(target_corrupted):
                if block.grid_x == player_x and block.grid_y == player_y:
                    return False

        if self.is_laser_active_at(player_x, player_y, is_corrupted=target_corrupted):
            return False

        return True

    def toggle_shift(self, player_x: int, player_y: int) -> bool:
        if self.can_shift(player_x, player_y):
            self.is_corrupted = not self.is_corrupted
            return True
        return False

    def update(self, player_x: int, player_y: int) -> tuple[bool, bool]:
        """Updates blocks, daemons, pressure plates, terminals, and win condition."""
        # 1. Update smooth block & daemon sliding
        for block in self.blocks:
            block.update()
        for daemon in self.daemons:
            daemon.update()

        # 2. Update Pressure Plates
        plate_clicked = False
        for plate in self.plates:
            if plate.update(player_x, player_y, self.blocks, self.is_corrupted):
                plate_clicked = True

        # 3. Check terminals
        reboot_occurred = False
        for terminal in self.terminals:
            if terminal.check_interaction(player_x, player_y, self.is_corrupted):
                reboot_occurred = True

        # 4. Check win condition
        if self.exit_door.is_entered(player_x, player_y, self.all_terminals_rebooted):
            self.is_won = True

        return reboot_occurred, plate_clicked

    def draw(self, surface: pygame.Surface):
        bg_color = COLOR_BG_CORRUPT if self.is_corrupted else COLOR_BG_NORMAL
        wall_color = COLOR_WALL_CORRUPT if self.is_corrupted else COLOR_WALL_NORMAL
        border_color = COLOR_WALL_BORDER_CORRUPT if self.is_corrupted else COLOR_WALL_BORDER_NORMAL

        surface.fill(bg_color)

        # 1. Walls
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.current_map[y][x] == 1:
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(surface, wall_color, rect, border_radius=4)
                    pygame.draw.rect(surface, border_color, rect, width=2, border_radius=4)

        # 2. Floor Pressure Plates
        for plate in self.plates:
            plate.draw(surface, self.is_corrupted)

        # 3. Exit Door
        self.exit_door.draw(surface, is_open=self.all_terminals_rebooted)

        # 4. Terminals
        for terminal in self.terminals:
            terminal.draw(surface, self.is_corrupted)

        # 5. RAM Blocks
        for block in self.blocks:
            block.draw(surface, self.is_corrupted)

        # 6. Laser Barriers
        channels = self.active_channels
        for laser in self.lasers:
            laser.draw(surface, self.is_corrupted, channels)

        # 7. Daemons / Sentinels
        for daemon in self.daemons:
            daemon.draw(surface, self.is_corrupted)
