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
from src.interactables import Terminal, ExitDoor
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

        # Instantiate terminals from level metadata
        self.terminals = [
            Terminal(t["x"], t["y"], required_in_corrupt=t["corrupted"])
            for t in data["terminals"]
        ]
        
        # Instantiate exit
        exit_x, exit_y = data["exit_pos"]
        self.exit_door = ExitDoor(exit_x, exit_y)

    @property
    def current_map(self) -> list[list[int]]:
        return self.corrupt_map if self.is_corrupted else self.normal_map

    @property
    def all_terminals_rebooted(self) -> bool:
        return all(t.rebooted for t in self.terminals)

    def can_shift(self, player_x: int, player_y: int) -> bool:
        target_map = self.normal_map if self.is_corrupted else self.corrupt_map
        return target_map[player_y][player_x] == 0

    def toggle_shift(self, player_x: int, player_y: int) -> bool:
        if self.can_shift(player_x, player_y):
            self.is_corrupted = not self.is_corrupted
            return True
        return False

    def is_solid(self, grid_x: int, grid_y: int) -> bool:
        if not (0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT):
            return True
        return self.current_map[grid_y][grid_x] == 1

    def update(self, player_x: int, player_y: int):
        for terminal in self.terminals:
            terminal.check_interaction(player_x, player_y, self.is_corrupted)

        if self.exit_door.is_entered(player_x, player_y, self.all_terminals_rebooted):
            self.is_won = True

    def draw(self, surface: pygame.Surface):
        bg_color = COLOR_BG_CORRUPT if self.is_corrupted else COLOR_BG_NORMAL
        wall_color = COLOR_WALL_CORRUPT if self.is_corrupted else COLOR_WALL_NORMAL
        border_color = COLOR_WALL_BORDER_CORRUPT if self.is_corrupted else COLOR_WALL_BORDER_NORMAL

        surface.fill(bg_color)

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.current_map[y][x] == 1:
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(surface, wall_color, rect, border_radius=4)
                    pygame.draw.rect(surface, border_color, rect, width=2, border_radius=4)

        self.exit_door.draw(surface, is_open=self.all_terminals_rebooted)
        for terminal in self.terminals:
            terminal.draw(surface, self.is_corrupted)