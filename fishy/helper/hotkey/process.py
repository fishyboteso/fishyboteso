import time
from enum import Enum

import keyboard
import mouse


class Key(Enum):
    F9 = "f9"
    LMB = "left"


mouse_buttons = [Key.LMB]


def _mouse_callback(queue):
    def callback(e):
        # noinspection PyProtectedMember
        if not (type(e) == mouse.ButtonEvent and e.event_type == "up" and e.button in Key._value2member_map_):
            return

        # call the parent function here
        queue.put(Key(e.button))

    return callback


def _keyboard_callback(queue, k):
    def callback():
        queue.put(k)

    return callback


def run(inq, outq):
    mouse.hook(_mouse_callback(outq))
    for k in Key:
        if k not in mouse_buttons:
            keyboard.add_hotkey(k.value, _keyboard_callback(outq, k))

    stop = False
    while not stop:
        if inq.get() == "stop":
            stop = True
        time.sleep(1)
