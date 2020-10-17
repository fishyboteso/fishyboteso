import math
import logging
import time

from fishy.engine.fullautofisher.engine import FullAuto
from pynput import keyboard, mouse

from fishy.helper import hotkey
from fishy.helper.config import config
from fishy.helper.helper import wait_until
from fishy.helper.hotkey import Key

mse = mouse.Controller()
kb = keyboard.Controller()

"""
-1 callibrating speed and rotation, 
0, waiting for looking up and first f8, 
1, waiting for reaching down and second f8, 
2 done
"""


class Calibrate():
    def __init__(self, engine: FullAuto):
        self._callibrate_state = -1
        self.engine = engine

    def f8_pressed(self):
        self._callibrate_state += 1

    def callibrate(self):
        logging.debug("Callibrating...")
        _callibrate_state = -1

        walking_time = 3
        rotate_times = 50

        # region rotate and move
        coods = self.engine.get_coods()
        if coods is None:
            return

        x1, y1, rot1 = coods

        kb.press('w')
        time.sleep(walking_time)
        kb.release('w')
        time.sleep(0.5)

        coods = self.engine.get_coods()
        if coods is None:
            return
        x2, y2, rot2 = coods

        for _ in range(rotate_times):
            mse.move(FullAuto.rotate_by, 0)
            time.sleep(0.05)

        coods = self.engine.get_coods()
        if coods is None:
            return
        x3, y3, rot3 = coods

        if rot3 > rot2:
            rot3 -= 360

        move_factor = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / walking_time
        rot_factor = (rot3 - rot2) / rotate_times
        # endregion

        logging.info("Now loop up and press f8")

        hotkey.set_hotkey(Key.F8, self.f8_pressed)

        wait_until(lambda: self._callibrate_state == 1)

        logging.info("looking down now, as soon as you look on the floor, press f8 again")

        y_cal_start_time = time.time()
        while self._callibrate_state == 1:
            mse.move(0, FullAuto.rotate_by)
            time.sleep(0.05)

        time_to_reach_bottom = time.time() - y_cal_start_time

        self.engine.factors = move_factor, rot_factor, time_to_reach_bottom
        config.set("full_auto_factors", self.engine.factors)
        logging.info(self.engine.factors)

        hotkey.free_key(Key.F8)
