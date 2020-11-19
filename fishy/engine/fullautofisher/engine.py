import math
import os
import tempfile
import traceback
import uuid
from enum import Enum
from zipfile import ZipFile

import cv2
import logging
import time

import numpy as np
import pytesseract

from fishy.engine.fullautofisher.tesseract import is_tesseract_installed, downlaoad_and_extract_tesseract, \
    get_values_from_image
from fishy.engine.semifisher.fishing_mode import FishingMode

from fishy.engine import SemiFisherEngine
from fishy.engine.common.window import WindowClient
from fishy.engine.semifisher import fishing_mode, fishing_event

from fishy.engine.common.IEngine import IEngine
from pynput import keyboard, mouse

from fishy.helper import hotkey, helper
from fishy.helper.config import config
from fishy.helper.downloader import download_file_from_google_drive
from fishy.helper.helper import sign
from fishy.helper.hotkey import Key

mse = mouse.Controller()
kb = keyboard.Controller()


def image_pre_process(img):
    scale_percent = 200  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    img = cv2.bitwise_not(img)
    return img


class State(Enum):
    NONE = 0
    PLAYING = 1
    RECORDING = 2
    OTHER = 3


class FullAuto(IEngine):
    rotate_by = 30
    state = State.NONE

    def __init__(self, gui_ref):
        from fishy.engine.fullautofisher.controls import Controls
        from fishy.engine.fullautofisher import controls
        from fishy.engine.fullautofisher.calibrate import Calibrate
        from fishy.engine.fullautofisher.test import Test

        super().__init__(gui_ref)
        self._hole_found_flag = False
        self._curr_rotate_y = 0

        self.fisher = SemiFisherEngine(None)
        self.calibrate = Calibrate(self)
        self.test = Test(self)
        self.controls = Controls(controls.get_controls(self))

    @property
    def show_crop(self):
        return config.get("show_window_full_auto", False)

    @show_crop.setter
    def show_crop(self, x):
        config.set("show_window_full_auto", x)

    def run(self):
        logging.info("Loading please wait...")
        self.gui.bot_started(True)
        fishing_event.unsubscribe()
        self.fisher.toggle_start()

        self.window = WindowClient(color=cv2.COLOR_RGB2GRAY, show_name="Full auto debug")

        try:
            if self.calibrate.crop is None:
                self.calibrate.update_crop(enable_crop=False)
            self.window.crop = self.calibrate.crop

            if not is_tesseract_installed():
                logging.info("tesseract not found")
                downlaoad_and_extract_tesseract()

            self.controls.initialize()
            while self.start and WindowClient.running():
                self.window.show(self.show_crop, func=image_pre_process)
                if not self.show_crop:
                    time.sleep(0.1)
        except:
            traceback.print_exc()

            if not self.window.get_capture():
                logging.error("Game window not found")

        self.gui.bot_started(False)
        self.controls.unassign_keys()
        self.window.show(False)
        logging.info("Quitting")
        self.window.destory()
        self.fisher.toggle_start()

    def get_coods(self):
        img = self.window.processed_image(func=image_pre_process)
        return get_values_from_image(img)

    def move_to(self, target):
        if target is None:
            logging.error("set target first")
            return

        if not self.calibrate.all_callibrated():
            logging.error("you need to callibrate first")
            return

        current = self.get_coods()
        print(f"Moving from {(current[0], current[1])} to {target}")
        move_vec = target[0] - current[0], target[1] - current[1]

        dist = math.sqrt(move_vec[0] ** 2 + move_vec[1] ** 2)
        print(f"distance: {dist}")
        if dist < 5e-05:
            print("distance very small skipping")
            return

        target_angle = math.degrees(math.atan2(-move_vec[1], move_vec[0])) + 90
        from_angle = current[2]

        self.rotate_to(target_angle, from_angle)

        walking_time = dist / self.calibrate.move_factor
        print(f"walking for {walking_time}")
        kb.press('w')
        time.sleep(walking_time)
        kb.release('w')
        print("done")

    def rotate_to(self, target_angle, from_angle=None):
        if from_angle is None:
            _, _, from_angle = self.get_coods()

        if target_angle < 0:
            target_angle = 360 + target_angle
        while target_angle > 360:
            target_angle -= 360
        print(f"Rotating from {from_angle} to {target_angle}")

        angle_diff = target_angle - from_angle

        if abs(angle_diff) > 180:
            angle_diff = (360 - abs(angle_diff)) * sign(angle_diff) * -1

        rotate_times = int(angle_diff / self.calibrate.rot_factor) * -1

        print(f"rotate_times: {rotate_times}")

        for _ in range(abs(rotate_times)):
            mse.move(sign(rotate_times) * FullAuto.rotate_by * -1, 0)
            time.sleep(0.05)

    def look_for_hole(self):
        self._hole_found_flag = False

        if FishingMode.CurrentMode == fishing_mode.State.LOOK:
            return True

        def found_hole(e):
            if e == fishing_mode.State.LOOK:
                self._hole_found_flag = True

        fishing_mode.subscribers.append(found_hole)

        t = 0
        while not self._hole_found_flag and t <= self.calibrate.time_to_reach_bottom / 3:
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

    def rotate_back(self):
        while self._curr_rotate_y > 0.01:
            mse.move(0, -FullAuto.rotate_by)
            time.sleep(0.05)
            self._curr_rotate_y -= 0.05


if __name__ == '__main__':
    logging.getLogger("").setLevel(logging.DEBUG)
    hotkey.initalize()
    # noinspection PyTypeChecker
    bot = FullAuto(None)
    bot.toggle_start()
