import math
import cv2
import logging
import time

import numpy as np
import pywintypes
import pytesseract

from fishy.engine.IEngine import IEngine
from fishy.engine.window import Window
from pynput import keyboard, mouse

from fishy.helper import Config, hotkey

mse = mouse.Controller()
kb = keyboard.Controller()

rotate_by = 30


def sign(x):
    return -1 if x < 0 else 1


def get_crop_coods(window):
    Window.loop()
    img = window.get_capture()
    img = cv2.inRange(img, 0, 1)
    Window.loop_end()

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
            return x, y, x + w, y + h


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
    keys = ["up", "down", "left", "right"]
    for k in keys:
        hotkey.free_key(k)


class FullAuto(IEngine):
    def __init__(self, config, gui_ref):
        super().__init__(config, gui_ref)
        self.factors = self.config.get("full_auto_factors", None)
        self.tesseract_dir = None
        self.target = None

        if self.factors is None:
            logging.warning("Please callibrate first")

    def run(self):
        logging.info("Loading please wait...")
        self.initalize_keys()

        try:
            Window.init(False)
        except pywintypes.error:
            logging.info("Game window not found")
            self.toggle_start()
            return

        self.window = Window(color=cv2.COLOR_RGB2GRAY)
        self.window.crop = get_crop_coods(self.window)
        self.tesseract_dir = self.config.get("tesseract_dir", None)

        if self.tesseract_dir is None:
            logging.warning("Can't start without Tesseract Directory")
            self.gui.bot_started(False)
            self.toggle_start()
            return

        if self.get_gui is not None:
            self.gui.bot_started(True)

        logging.info("Controlls:\nUP: Callibrate\nLEFT: Print Coordinates\nDOWN: Set target\nRIGHT: Move to target")
        while self.start:
            Window.loop()

            # self.window.show("test", func=image_pre_process)
            Window.loop_end()
        self.gui.bot_started(False)
        unassign_keys()

    def get_coods(self):
        return get_values_from_image(self.window.processed_image(func=image_pre_process), self.tesseract_dir)

    def callibrate(self):
        logging.debug("Callibrating...")
        walking_time = 3
        rotate_times = 50

        coods = self.get_coods()
        if coods is None:
            return

        x1, y1, rot1 = coods

        kb.press('w')
        time.sleep(walking_time)
        kb.release('w')
        time.sleep(0.5)

        coods = self.get_coods()
        if coods is None:
            return
        x2, y2, rot2 = coods

        for _ in range(rotate_times):
            mse.move(rotate_by, 0)
            time.sleep(0.05)

        coods = self.get_coods()
        if coods is None:
            return
        x3, y3, rot3 = coods

        if rot3 > rot2:
            rot3 -= 360

        rot_factor = (rot3 - rot2) / rotate_times
        move_factor = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / walking_time
        self.config.set("full_auto_factors", (move_factor, rot_factor))
        self.factors = move_factor, rot_factor
        logging.info(self.factors)

    def move_to(self, target):
        if target is None:
            logging.error("set target first")
            return

        if self.factors is None:
            logging.error("you need to callibrate first")
            return

        current = self.get_coods()
        print(f"Moving from {(current[0], current[1])} to {self.target}")
        move_vec = target[0] - current[0], target[1] - current[1]
        target_angle = math.degrees(math.atan2(-move_vec[1], move_vec[0]))
        if target_angle < 0:
            target_angle = 360 + target_angle
        target_angle += 90
        while target_angle > 360:
            target_angle -= 360
        print(f"Rotating from {current[2]} to {target_angle}")

        angle_diff = target_angle - current[2]

        if abs(angle_diff) > 180:
            angle_diff = (360 - abs(angle_diff)) * sign(angle_diff) * -1

        rotate_times = int(angle_diff / self.factors[1]) * -1
        walking_time = math.sqrt(move_vec[0] ** 2 + move_vec[1] ** 2) / self.factors[0]

        print(f"Rotating by {angle_diff}\nrotate_times {rotate_times}\nwalking_time {walking_time}")

        for _ in range(abs(rotate_times)):
            mse.move(sign(rotate_times) * rotate_by * -1, 0)
            time.sleep(0.05)

        kb.press('w')
        time.sleep(walking_time)
        kb.release('w')
        print("done")

    def initalize_keys(self):
        hotkey.set_hotkey("left", lambda: logging.info(self.get_coods()))
        hotkey.set_hotkey("up", lambda: self.callibrate())

        def down():
            t = self.get_coods()[:-1]
            self.config.set("target", t)
            print(f"target_coods are {t}")
        hotkey.set_hotkey("down", down)

        hotkey.set_hotkey("right", lambda: self.move_to(self.config.get("target", None)))


if __name__ == '__main__':
    logging.getLogger("").setLevel(logging.DEBUG)
    # noinspection PyTypeChecker
    bot = FullAuto(Config(), None)
    hotkey.initalize()
    bot.toggle_start()
