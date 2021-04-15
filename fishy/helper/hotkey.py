from enum import Enum
from threading import Thread
from typing import Dict, Callable, Optional

import keyboard


class Key(Enum):
    F9 = "f9"
    F10 = "f10"
    F8 = "f8"
    F7 = "f7"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


_hotkeys: Dict[Key, Optional[Callable]] = {}


def _get_callback(k):
    def callback():
        if not _hotkeys[k]:
            return

        Thread(target=_hotkeys[k]).start()
    return callback


def initalize():
    for k in Key:
        _hotkeys[k] = None
        keyboard.add_hotkey(k.value, _get_callback(k))


def set_hotkey(key: Key, func: Optional[Callable]):
    _hotkeys[key] = func


def free_key(k: Key):
    set_hotkey(k, None)
