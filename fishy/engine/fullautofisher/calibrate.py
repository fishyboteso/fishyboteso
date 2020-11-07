import math
import logging
import time

import cv2
import numpy as np

from fishy.engine.fullautofisher.engine import FullAuto
from pynput import keyboard, mouse

from fishy.helper import hotkey
from fishy.helper.config import config
from fishy.helper.helper import wait_until
from fishy.helper.hotkey import Key

mse = mouse.Controller()
kb = keyboard.Controller()

offset = 0


def get_crop_coods(window):
    img = window.get_capture()
    img = cv2.inRange(img, 0, 1)

    cnt, h = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    """
    code from https://stackoverflow.com/a/45770227/4512396
    """
    for i in range(len(cnt)):
        area = cv2.contourArea(cnt[i])
        if 5000 < area < 100000:
            mask = np.zeros_like(img)
            cv2.drawContours(mask, cnt, i, 255, -1)
            x, y, w, h = cv2.boundingRect(cnt[i])
            return x, y + offset, x + w, y + h - offset


def _update_factor(key, value):
    full_auto_factors = config.get("full_auto_factors", {})
    full_auto_factors[key] = value
    config.set("full_auto_factors", full_auto_factors)


def _get_factor(key):
    config.get("full_auto_factors", {}).get(key)


class Calibrate:
    def __init__(self, engine: FullAuto):
        self._callibrate_state = -1
        self.engine = engine

    # region getters
    @property
    def crop(self):
        return _get_factor("crop")

    @property
    def move_factor(self):
        return _get_factor("move_factor")

    @property
    def rot_factor(self):
        return _get_factor("rot_factor")

    @property
    def time_to_reach_bottom(self):
        return _get_factor("time_to_reach_bottom")

    # endregion

    def all_callibrated(self):
        return self.crop and self.move_factor and self.rot_factor

    def toggle_show(self):
        self.engine.show_crop = not self.engine.show_crop

    def update_crop(self, enable_crop=True):
        if enable_crop:
            self.engine.show_crop = True
        crop = get_crop_coods(self.engine.window)
        self.engine.window.crop = self.engine.crop
        _update_factor("crop", crop)

    def walk_calibrate(self):
        walking_time = 3

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

        move_factor = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / walking_time
        _update_factor("move_factor", move_factor)

    def rotate_calibrate(self):
        rotate_times = 50

        coods = self.engine.get_coods()
        if coods is None:
            return
        _, _, rot2 = coods

        for _ in range(rotate_times):
            mse.move(FullAuto.rotate_by, 0)
            time.sleep(0.05)

        coods = self.engine.get_coods()
        if coods is None:
            return
        x3, y3, rot3 = coods

        if rot3 > rot2:
            rot3 -= 360

        rot_factor = (rot3 - rot2) / rotate_times
        _update_factor("rot_factor", rot_factor)

    def time_to_reach_bottom_callibrate(self):
        self._callibrate_state = 0

        def _f8_pressed():
            self._callibrate_state += 1

        logging.info("Now loop up and press f8")
        hotkey.set_hotkey(Key.F8, _f8_pressed)

        wait_until(lambda: self._callibrate_state == 1)

        logging.info("looking down now, as soon as you look on the floor, press f8 again")

        y_cal_start_time = time.time()
        while self._callibrate_state == 1:
            mse.move(0, FullAuto.rotate_by)
            time.sleep(0.05)
        hotkey.free_key(Key.F8)

        time_to_reach_bottom = time.time() - y_cal_start_time
        _update_factor("time_to_reach_bottom", time_to_reach_bottom)
