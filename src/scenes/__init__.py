"""
Scenes package for Shift/Return.
Exposes all individual scene classes and state representations for seamless importing.
"""
from src.scenes.base import Scene, StateSnapshot
from src.scenes.title_scene import TitleScene
from src.scenes.game_scene import GameScene
from src.scenes.pause_scene import PauseScene
from src.scenes.level_clear_scene import LevelClearScene
from src.scenes.level_select_scene import LevelSelectScene

__all__ = [
    "Scene",
    "StateSnapshot",
    "TitleScene",
    "GameScene",
    "PauseScene",
    "LevelClearScene",
    "LevelSelectScene",
]
