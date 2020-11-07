import logging

from fishy.helper import hotkey

from fishy.engine.fullautofisher.engine import FullAuto
from fishy.helper.config import config
from fishy.helper.hotkey import Key


def get_controls(engine: FullAuto):
    from fishy.engine.fullautofisher.calibrate import Calibrate
    from fishy.engine.fullautofisher.recorder import Recorder
    from fishy.engine.fullautofisher.player import Player

    controls = [
        # ("MAIN", {
        #     Key.RIGHT: Player(engine).start_route,
        #     Key.UP: Calibrate(engine).callibrate,
        #     Key.LEFT: Recorder(engine).start_recording,
        #     Key.DOWN: change_state
        # }),
        # ("COODS", {
        #     Key.RIGHT: print_coods,
        #     Key.UP: engine.update_crop,
        #     Key.LEFT: toggle_show,
        #     Key.DOWN: change_state
        # }),
        # ("TEST1", {
        #     Key.RIGHT: set_target,
        #     Key.UP: rotate_to_90,
        #     Key.LEFT: move_to_target,
        #     Key.DOWN: change_state
        # })
    ]

    return controls


class Controls:
    def __init__(self, controls, first=0):
        self.current_menu = first - 1
        self.controls = controls

    def change_state(self):
        self.current_menu += 1
        if self.current_menu == len(self.controls):
            self.current_menu = 0

        help_str = F"CONTROLS: {self.controls[self.current_menu][0]}"
        for key, func in self.controls[self.current_menu][1].items():
            hotkey.set_hotkey(key, func)
            help_str += f"\n{key.value}: {func.__name__}"
        logging.info(help_str)

    def unassign_keys(self):
        keys = []
        for c in self.controls:
            for k in c[1].keys():
                if k not in keys:
                    hotkey.free_key(k)