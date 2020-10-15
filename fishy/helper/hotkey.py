from enum import Enum
from typing import Dict, Callable

import keyboard

from fishy.helper import helper


class Key(Enum):
    F9 = "f9",
    F8 = "f8"
    F7 = "f7"
    UP = "up",
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


_hotkeys: Dict[Key, Callable] = {}


def _run_callback(k):
    return lambda: _hotkeys[k]()


def initalize():
    for k in Key:
        _hotkeys[k] = helper.empty_function
        keyboard.add_hotkey(k.value, _run_callback(k))


def set_hotkey(key: Key, func: Callable):
    _hotkeys[key] = func


def free_key(k: Key):
    set_hotkey(k, helper.empty_function)
