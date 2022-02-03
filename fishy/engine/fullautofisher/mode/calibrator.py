import logging
import math
import time
import typing

import cv2
import numpy as np

if typing.TYPE_CHECKING:
    from fishy.engine.fullautofisher.engine import FullAuto

from fishy.engine.fullautofisher.mode.imode import IMode
from pynput import keyboard, mouse

from fishy.helper.config import config

mse = mouse.Controller()
kb = keyboard.Controller()

offset = 0


def get_crop_coords(window):
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

    return None


def _update_factor(key, value):
    full_auto_factors = config.get("full_auto_factors", {})
    full_auto_factors[key] = value
    config.set("full_auto_factors", full_auto_factors)


def _get_factor(key):
    return config.get("full_auto_factors", {}).get(key)


class Calibrator(IMode):
    def __init__(self, engine: 'FullAuto'):
        self._callibrate_state = -1
        self.engine = engine

    @property
    def move_factor(self):
        return _get_factor("move_factor")

    @property
    def rot_factor(self):
        return _get_factor("rot_factor")

    # endregion

    def all_calibrated(self):
        return self.move_factor is not None and \
               self.rot_factor is not None and \
               self.move_factor != 0 and \
               self.rot_factor != 0

    def toggle_show(self):
        self.engine.show_crop = not self.engine.show_crop

    def _walk_calibrate(self):
        walking_time = 3

        coords = self.engine.get_coords()
        if coords is None:
            return

        x1, y1, rot1 = coords

        kb.press('w')
        time.sleep(walking_time)
        kb.release('w')
        time.sleep(0.5)

        coords = self.engine.get_coords()
        if coords is None:
            return
        x2, y2, rot2 = coords

        move_factor = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / walking_time
        _update_factor("move_factor", move_factor)
        logging.info(f"walk calibrate done, move_factor: {move_factor}")

    def _rotate_calibrate(self):
        from fishy.engine.fullautofisher.engine import FullAuto

        rotate_times = 50

        coods = self.engine.get_coords()
        if coods is None:
            return
        _, _, rot2 = coods

        for _ in range(rotate_times):
            mse.move(FullAuto.rotate_by, 0)
            time.sleep(0.05)

        coods = self.engine.get_coords()
        if coods is None:
            return
        x3, y3, rot3 = coods

        if rot3 > rot2:
            rot3 -= 360

        rot_factor = (rot3 - rot2) / rotate_times
        _update_factor("rot_factor", rot_factor)
        logging.info(f"rotate calibrate done, rot_factor: {rot_factor}")

    def run(self):
        self._walk_calibrate()
        self._rotate_calibrate()
        config.set("calibrate", False)
        logging.info("calibration done")
