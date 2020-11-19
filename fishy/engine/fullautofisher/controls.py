import logging

from fishy.helper import hotkey, helper

from fishy.engine.fullautofisher.engine import FullAuto
from fishy.helper.hotkey import Key


def get_controls(engine: FullAuto):
    from fishy.engine.fullautofisher.recorder import Recorder
    from fishy.engine.fullautofisher.player import Player

    controls = [
        ("MODE_SELECT", {
            Key.RIGHT: (lambda: engine.controls.select_mode("CALIBRATE"), "calibrate mode"),
            Key.UP: (lambda: engine.controls.select_mode("PLAY"), "play mode"),
            Key.LEFT: (lambda: engine.controls.select_mode("RECORD"), "record mode"),
            Key.DOWN: (lambda: engine.controls.select_mode("TEST"), "test mode")
        }),
        ("CALIBRATE", {
            Key.RIGHT: (engine.calibrate.update_crop, "cropping"),
            Key.UP: (engine.calibrate.walk_calibrate, "walking"),
            Key.LEFT: (engine.calibrate.rotate_calibrate, "rotation"),
            Key.DOWN: (engine.calibrate.time_to_reach_bottom_callibrate, "look up down")
        }),
        ("PLAY/RECORD", {
            Key.RIGHT: (Player(engine).toggle_move, "start/stop play"),
            Key.UP: (Recorder(engine).toggle_recording, "start/stop record"),
            Key.LEFT: (None, "not implemented"),
            Key.DOWN: (None, "not implemented")
        }),
        ("TEST1", {
            Key.RIGHT: (engine.test.print_coods, "print coordinates"),
            Key.UP: (engine.test.look_for_hole, "look for hole up down"),
            Key.LEFT: (None, "not implemented"),
            Key.DOWN: (lambda: engine.controls.select_mode("TEST2"), "show next")
        }),
        ("TEST2", {
            Key.RIGHT: (engine.test.set_target, "set target"),
            Key.UP: (engine.test.move_to_target, "move to target"),
            Key.LEFT: (engine.test.rotate_to_target, "rotate to target"),
            Key.DOWN: (lambda: engine.controls.select_mode("TEST1"), "show previous")
        })
    ]

    return controls


class Controls:
    def __init__(self, controls, first=0):
        self.current_menu = first - 1
        self.controls = controls

    def initialize(self):
        self.select_mode("MODE_SELECT")

    def select_mode(self, mode):
        self.current_menu = 0
        for i, control in enumerate(self.controls):
            if mode == control[0]:
                self.current_menu = i

        help_str = F"CONTROLS: {self.controls[self.current_menu][0]}"
        for key, meta in self.controls[self.current_menu][1].items():
            func, name = meta
            hotkey.set_hotkey(key, func)
            help_str += f"\n{key.value}: {name}"
        logging.info(help_str)

    def unassign_keys(self):
        keys = []
        for c in self.controls:
            for k in c[1].keys():
                if k not in keys:
                    hotkey.free_key(k)