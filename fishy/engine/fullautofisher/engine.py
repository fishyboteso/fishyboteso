import math
import uuid

import cv2
import logging
import time

import numpy as np
import pytesseract
from fishy.engine.semifisher.fishing_mode import FishingMode

from fishy.engine import SemiFisherEngine
from fishy.engine.common.window import WindowClient
from fishy.engine.semifisher import fishing_mode, fishing_event

from fishy.engine.common.IEngine import IEngine
from pynput import keyboard, mouse

from fishy.helper import hotkey, helper
from fishy.helper.config import config
from fishy.helper.hotkey import Key

mse = mouse.Controller()
kb = keyboard.Controller()
offset = 0


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
        text = text.replace(" ", "")
        vals = text.split(":")
        return float(vals[0]), float(vals[1]), float(vals[2])
    except Exception:
        logging.error("Couldn't read coods")
        cv2.imwrite(f"fail_{str(uuid.uuid4())[:8]}", img)
        return None


class FullAuto(IEngine):
    rotate_by = 30

    def __init__(self, gui_ref):
        super().__init__(gui_ref)
        self.factors = config.get("full_auto_factors", None)
        self._tesseract_dir = None
        self._target = None
        self.crop = config.get("full_auto_crop")

        if self.factors is None:
            logging.warning("Please callibrate first")

        self._hole_found_flag = False
        self._curr_rotate_y = 0

        self.fisher = SemiFisherEngine(None)
        self.controls = Controls(self.get_controls())

    @property
    def show(self):
        return config.get("show_window_full_auto", False)

    @show.setter
    def show(self, x):
        config.set("show_window_full_auto", x)

    def update_crop(self):
        self.show = True
        self.crop = get_crop_coods(self.window)
        config.set("full_auto_crop", self.crop)
        self.window.crop = self.crop

    def run(self):
        logging.info("Loading please wait...")
        fishing_event.unsubscribe()
        self.fisher.toggle_start()
        self.controls.change_state()

        self.window = WindowClient(color=cv2.COLOR_RGB2GRAY, show_name="Full auto debug")
        if self.crop is None:
            self.update_crop()
        self.window.crop = self.crop

        self._tesseract_dir = config.get("tesseract_dir", None)
        if self._tesseract_dir is None:
            logging.warning("Can't start without Tesseract Directory")
            self.gui.bot_started(False)
            self.toggle_start()
            return

        self.gui.bot_started(True)

        while self.start and WindowClient.running():
            self.window.show(self.show, func=image_pre_process)
            if not self.show:
                time.sleep(0.1)

        self.gui.bot_started(False)
        self.controls.unassign_keys()
        self.window.show(False)
        logging.info("Quit")
        self.window.destory()
        self.fisher.toggle_start()

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

        walking_time = dist / self.factors[0]
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

        rotate_times = int(angle_diff / self.factors[1]) * -1

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
        while not self._hole_found_flag and t <= self.factors[2] / 3:
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

    def get_controls(self):
        from fishy.engine.fullautofisher.calibrate import Calibrate
        from fishy.engine.fullautofisher.recorder import Recorder
        from fishy.engine.fullautofisher.player import Player

        def change_state():
            self.controls.change_state()

        def print_coods():
            logging.info(self.get_coods())

        def set_target():
            t = self.get_coods()[:-1]
            config.set("target", t)
            print(f"target_coods are {t}")

        def move_to_target():
            self.move_to(config.get("target"))

        def rotate_to_90():
            self.rotate_to(90)

        def toggle_show():
            self.show = not self.show

        controls = [
            ("MAIN", {
                Key.RIGHT: Player(self).start_route,
                Key.UP: Calibrate(self).callibrate,
                Key.LEFT: Recorder(self).start_recording,
                Key.DOWN: change_state
            }),
            ("COODS", {
                Key.RIGHT: print_coods,
                Key.UP: self.update_crop,
                Key.LEFT: toggle_show,
                Key.DOWN: change_state
            }),
            ("TEST1", {
                Key.RIGHT: set_target,
                Key.UP: rotate_to_90,
                Key.LEFT: move_to_target,
                Key.DOWN: change_state
            })
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


if __name__ == '__main__':
    logging.getLogger("").setLevel(logging.DEBUG)
    hotkey.initalize()
    # noinspection PyTypeChecker
    bot = FullAuto(None)
    bot.toggle_start()
