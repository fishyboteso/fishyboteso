import math
import traceback
from threading import Thread

import cv2
import logging
import time

from fishy.constants import libgps, fishyqr, lam2
from fishy.engine.fullautofisher.mode.calibrator import Calibrator
from fishy.engine.fullautofisher.mode.imode import FullAutoMode
from fishy.engine.fullautofisher.mode.player import Player
from fishy.engine.fullautofisher.mode.recorder import Recorder
from fishy.engine.fullautofisher.qr_detection import get_values_from_image, get_qr_location
from fishy.engine.semifisher.fishing_mode import FishingMode

from fishy.engine import SemiFisherEngine
from fishy.engine.common.window import WindowClient
from fishy.engine.semifisher import fishing_mode, fishing_event

from fishy.engine.common.IEngine import IEngine
from pynput import keyboard, mouse

from fishy.helper import hotkey, helper
from fishy.helper.helper import sign, log_raise
from fishy.helper.config import config

mse = mouse.Controller()
kb = keyboard.Controller()


def image_pre_process(img):
    scale_percent = 100  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return img


class FullAuto(IEngine):
    rotate_by = 30

    def __init__(self, gui_ref):
        from fishy.engine.fullautofisher.mode.calibrator import Calibrator
        from fishy.engine.fullautofisher.test import Test

        super().__init__(gui_ref)
        self._hole_found_flag = False
        self._curr_rotate_y = 0

        self.fisher = SemiFisherEngine(None)
        self.calibrator = Calibrator(self)
        self.test = Test(self)
        self.show_crop = False

        self.mode = None

    def run(self):

        addons_req = [libgps, lam2, fishyqr]
        for addon in addons_req:
            if not helper.addon_exists(*addon):
                helper.install_addon(*addon)

        self.gui.bot_started(True)
        self.window = WindowClient(color=cv2.COLOR_RGB2GRAY, show_name="Full auto debug")

        self.mode = None
        if config.get("calibrate", False):
            self.mode = Calibrator(self)
        elif FullAutoMode(config.get("full_auto_mode", 0)) == FullAutoMode.Player:
            self.mode = Player(self)
        elif FullAutoMode(config.get("full_auto_mode", 0)) == FullAutoMode.Recorder:
            self.mode = Recorder(self)

        # noinspection PyBroadException
        try:
            if self.window.get_capture() is None:
                log_raise("Game window not found")

            self.window.crop = get_qr_location(self.window.get_capture())
            if self.window.crop is None:
                log_raise("FishyQR not found")

            if not self.calibrator.all_callibrated():
                log_raise("you need to calibrate first")

            self.fisher.toggle_start()
            fishing_event.unsubscribe()
            if self.show_crop:
                self.start_show()

            self.mode.run()

        except Exception:
            traceback.print_exc()
            self.start = False

        self.gui.bot_started(False)
        self.window.show(False)
        logging.info("Quitting")
        self.window.destory()
        self.fisher.toggle_start()

    def start_show(self):
        def func():
            while self.start and WindowClient.running():
                self.window.show(self.show_crop, func=image_pre_process)
        Thread(target=func).start()

    def get_coods(self):
        img = self.window.processed_image(func=image_pre_process)
        return get_values_from_image(img)

    def move_to(self, target):
        if target is None:
            logging.error("set target first")
            return

        if not self.calibrator.all_callibrated():
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

        walking_time = dist / self.calibrator.move_factor
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

        rotate_times = int(angle_diff / self.calibrator.rot_factor) * -1

        print(f"rotate_times: {rotate_times}")

        for _ in range(abs(rotate_times)):
            mse.move(sign(rotate_times) * FullAuto.rotate_by * -1, 0)
            time.sleep(0.05)

    def look_for_hole(self):
        self._hole_found_flag = False

        if FishingMode.CurrentMode == fishing_mode.State.LOOKING:
            return True

        def found_hole(e):
            if e == fishing_mode.State.LOOKING:
                self._hole_found_flag = True

        fishing_mode.subscribers.append(found_hole)

        t = 0
        while not self._hole_found_flag and t <= 1.25:
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

    def toggle_start(self):
        self.start = not self.start
        if self.start:
            self.thread = Thread(target=self.run)
            self.thread.start()


if __name__ == '__main__':
    logging.getLogger("").setLevel(logging.DEBUG)
    hotkey.initalize()
    # noinspection PyTypeChecker
    bot = FullAuto(None)
    bot.toggle_start()
