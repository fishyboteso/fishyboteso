import math

import cv2
import logging
import time

import numpy as np
import pytesseract

from fishy.engine import SemiFisherEngine
from fishy.engine.common.window import WindowClient
from fishy.engine.semifisher import fishing_mode

from fishy.engine.common.IEngine import IEngine
from pynput import keyboard, mouse

from fishy.helper import hotkey
from fishy.helper.config import config
from fishy.helper.hotkey import Key

mse = mouse.Controller()
kb = keyboard.Controller()
offset = 10


def sign(x):
    return -1 if x < 0 else 1


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


def image_pre_process(img):
    scale_percent = 200  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    img = cv2.bitwise_not(img)
    return img


# noinspection PyBroadException
def get_values_from_image(img, tesseract_dir):
    try:
        pytesseract.pytesseract.tesseract_cmd = tesseract_dir + '/tesseract.exe'
        tessdata_dir_config = f'--tessdata-dir "{tesseract_dir}" -c tessedit_char_whitelist=0123456789.'

        text = pytesseract.image_to_string(img, lang="eng", config=tessdata_dir_config)
        vals = text.split(":")
        return float(vals[0]), float(vals[1]), float(vals[2])
    except Exception:
        logging.error("Couldn't read coods")
        return None


def unassign_keys():
    keys = [Key.UP, Key.RIGHT, Key.LEFT, Key.RIGHT]
    for k in keys:
        hotkey.free_key(k)


class FullAuto(IEngine):
    rotate_by = 30

    def __init__(self, gui_ref):
        super().__init__(gui_ref)
        self.factors = config.get("full_auto_factors", None)
        self._tesseract_dir = None
        self._target = None

        if self.factors is None:
            logging.warning("Please callibrate first")

        self._hole_found_flag = False
        self._curr_rotate_y = 0

    def run(self):
        logging.info("Loading please wait...")
        self.initalize_keys()

        self.window = WindowClient(color=cv2.COLOR_RGB2GRAY, show_name="Full auto debug")
        self.window.crop = get_crop_coods(self.window)
        self._tesseract_dir = config.get("tesseract_dir", None)

        if self._tesseract_dir is None:
            logging.warning("Can't start without Tesseract Directory")
            self.gui.bot_started(False)
            self.toggle_start()
            return

        self.gui.bot_started(True)

        while self.start:
            self.window.show(func=image_pre_process)
            cv2.waitKey(25)
        self.gui.bot_started(False)
        unassign_keys()
        logging.info("Quit")

    def get_coods(self):
        return get_values_from_image(self.window.processed_image(func=image_pre_process), self._tesseract_dir)

    def move_to(self, target):
        if target is None:
            logging.error("set target first")
            return

        if self.factors is None:
            logging.error("you need to callibrate first")
            return

        current = self.get_coods()
        print(f"Moving from {(current[0], current[1])} to {self._target}")
        move_vec = target[0] - current[0], target[1] - current[1]
        target_angle = math.degrees(math.atan2(-move_vec[1], move_vec[0]))
        from_angle = current[2]

        self.rotate_to(target_angle, from_angle)

        walking_time = math.sqrt(move_vec[0] ** 2 + move_vec[1] ** 2) / self.factors[0]
        print(f"walking for {walking_time}")
        kb.press('w')
        time.sleep(walking_time)
        kb.release('w')
        print("done")

    def rotate_to(self, target_angle, from_angle=None):
        if target_angle is None:
            _, _, from_angle = self.get_coods()

        if target_angle < 0:
            target_angle = 360 + target_angle
        target_angle += 90
        while target_angle > 360:
            target_angle -= 360
        print(f"Rotating from {from_angle} to {target_angle}")

        angle_diff = target_angle - from_angle

        if abs(angle_diff) > 180:
            angle_diff = (360 - abs(angle_diff)) * sign(angle_diff) * -1

        rotate_times = int(angle_diff / self.factors[1]) * -1

        print(f"rotate_times: {rotate_times}")

        for _ in range(abs(rotate_times)):
            mse.move(sign(rotate_times) * FullAuto.rotate_by * -1, 0)
            time.sleep(0.05)

    def look_for_hole(self):
        self._hole_found_flag = False

        def found_hole(e):
            if e == "look":
                self._hole_found_flag = True

        fishing_mode.subscribers.append(found_hole)

        t = 0
        while not self._hole_found_flag and t <= self.factors[2] / 2:
            mse.move(0, FullAuto.rotate_by)
            time.sleep(0.05)
            t += 0.05
        while not self._hole_found_flag and t > 0:
            mse.move(0, -FullAuto.rotate_by)
            time.sleep(0.05)
            t -= 0.05

        self._curr_rotate_y = t
        fishing_mode.subscribers.remove(found_hole)
        return self._hole_found_flag

    def set_target(self):
        t = self.get_coods()[:-1]
        config.set("target", t)
        print(f"target_coods are {t}")

    def initalize_keys(self):

        hotkey.set_hotkey(Key.RIGHT, lambda: logging.info(self.get_coods()))
        from fishy.engine.fullautofisher.calibrate import Calibrate
        hotkey.set_hotkey(Key.UP, Calibrate(self).callibrate)

        hotkey.set_hotkey(Key.F9, lambda: print(self.look_for_hole()))

        # hotkey.set_hotkey(Key.DOWN, self.set_target)
        # hotkey.set_hotkey(Key.RIGHT, lambda: self.move_to(self.config.get("target", None)))

        from fishy.engine.fullautofisher.recorder import Recorder
        from fishy.engine.fullautofisher.player import Player
        hotkey.set_hotkey(Key.LEFT, Recorder(self).start_recording)
        hotkey.set_hotkey(Key.DOWN, Player(self).start_route)
        logging.info("STARTED")


if __name__ == '__main__':
    logging.getLogger("").setLevel(logging.DEBUG)
    # noinspection PyTypeChecker
    bot = FullAuto(None)
    fisher = SemiFisherEngine(None)
    hotkey.initalize()
    fisher.toggle_start()
    bot.toggle_start()
