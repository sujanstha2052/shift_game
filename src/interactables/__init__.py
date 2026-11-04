"""
Interactables package for Shift/Return.
Exposes puzzle entities (terminals, doors, RAM blocks, pressure plates, lasers, daemons).
"""
from src.interactables.dimension import is_in_dimension
from src.interactables.terminal import Terminal
from src.interactables.exit_door import ExitDoor
from src.interactables.ram_block import RAMBlock
from src.interactables.circuit import PressurePlate, LaserBarrier
from src.interactables.daemon import DaemonSentinel

__all__ = [
    "is_in_dimension",
    "Terminal",
    "ExitDoor",
    "RAMBlock",
    "PressurePlate",
    "LaserBarrier",
    "DaemonSentinel",
]
