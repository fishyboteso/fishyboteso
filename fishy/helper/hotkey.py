import keyboard

from fishy.helper import helper

hotkeys = {"f9": helper.empty_function,
           "up": helper.empty_function,
           "down": helper.empty_function,
           "left": helper.empty_function,
           "right": helper.empty_function}


def set_hotkey(key, func):
    hotkeys[key] = func


def _run_callback(k):
    return lambda: hotkeys[k]()


def free_key(k):
    set_hotkey(k, helper.empty_function)


def initalize():
    for k in hotkeys.keys():
        keyboard.add_hotkey(k, _run_callback(k))
