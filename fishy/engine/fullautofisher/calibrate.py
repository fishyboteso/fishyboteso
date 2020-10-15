import math
import logging
import time

from fishy.engine.fullautofisher.engine import FullAuto
from pynput import keyboard, mouse

from fishy.helper import hotkey
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
_callibrate_state = -1


def callibrate(engine):
    global _callibrate_state

    logging.debug("Callibrating...")
    _callibrate_state = -1

    walking_time = 3
    rotate_times = 50

    # region rotate and move
    coods = engine.get_coods()
    if coods is None:
        return

    x1, y1, rot1 = coods

    kb.press('w')
    time.sleep(walking_time)
    kb.release('w')
    time.sleep(0.5)

    coods = engine.get_coods()
    if coods is None:
        return
    x2, y2, rot2 = coods

    for _ in range(rotate_times):
        mse.move(FullAuto.rotate_by, 0)
        time.sleep(0.05)

    coods = engine.get_coods()
    if coods is None:
        return
    x3, y3, rot3 = coods

    if rot3 > rot2:
        rot3 -= 360

    move_factor = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / walking_time
    rot_factor = (rot3 - rot2) / rotate_times
    # endregion

    logging.info("Now loop up and press f8, then as soon as the character looks down, press f8 again")

    def f8_pressed():
        global _callibrate_state
        _callibrate_state += 1

    hotkey.set_hotkey(Key.F8, f8_pressed)

    wait_until(lambda: _callibrate_state == 1)

    y_cal_start_time = time.time()
    while _callibrate_state == 1:
        mse.move(0, FullAuto.rotate_by)
        time.sleep(0.05)

    time_to_reach_bottom = time.time() - y_cal_start_time

    engine.factors = move_factor, rot_factor, time_to_reach_bottom
    engine.config.set("full_auto_factors", engine.factors)
    logging.info(engine.factors)

    hotkey.free_key(Key.F8)
