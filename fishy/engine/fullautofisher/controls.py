import logging

from pynput.keyboard import Key

from fishy.helper import hotkey

# todo: unused code remove it


def get_controls(controls: 'Controls'):
    controls = [
        ("MODE_SELECT", {
            Key.DOWN: (lambda: controls.select_mode("TEST1"), "test mode"),
        }),
        ("TEST1", {})
    ]

    return controls


class Controls:
    def __init__(self, controls, first=0):
        self.current_menu = first - 1
        self.controls = controls

    def initialize(self):
        self.select_mode(self.controls[0][0])

    def log_help(self):
        help_str = f"\nCONTROLS: {self.controls[self.current_menu][0]}"
        for key, meta in self.controls[self.current_menu][1].items():
            func, name = meta
            if func:
                hotkey.set_hotkey(key, func)
                help_str += f"\n{key.value}: {name}"
        logging.info(help_str)

    def select_mode(self, mode):
        self.current_menu = 0
        for i, control in enumerate(self.controls):
            if mode == control[0]:
                self.current_menu = i
        self.log_help()

    def unassign_keys(self):
        keys = []
        for c in self.controls:
            for k in c[1].keys():
                if k not in keys:
                    hotkey.free_key(k)
