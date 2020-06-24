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
from pynput.keyboard import Key

mse = mouse.Controller()
kb = keyboard.Controller()


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


def get_values_from_image(img):
    try:
        pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'
        tessdata_dir_config = '--tessdata-dir "C:/Program Files (x86)/Tesseract-OCR/" -c tessedit_char_whitelist=0123456789.'

        text = pytesseract.image_to_string(img, lang="eng", config=tessdata_dir_config)
        vals = text.split(":")
        return float(vals[0]), float(vals[1]), float(vals[2])
    except:
        logging.error("Couldn't read coods")
        return None


class FullAuto(IEngine):
    def __init__(self, config, gui_ref):
        super().__init__(config, gui_ref)
        self.factors = None

    def run(self):

        try:
            Window.init(False)
        except pywintypes.error:
            logging.info("Game window not found")
            self.start = False
            return

        self.window = Window(color=cv2.COLOR_RGB2GRAY)
        self.window.crop = get_crop_coods(self.window)

        time.sleep(2)

        if self.get_gui is not None:
            self.gui.bot_started(True)
        while self.start:
            Window.loop()

            self.window.show("test", func=image_pre_process)
            Window.loop_end()
        self.gui.bot_started(False)

    def get_coods(self):
        return get_values_from_image(self.window.processed_image(func=image_pre_process))

    def callibrate(self):
        logging.debug("Callibrating...")
        walking_time = 3
        rotate_by = 100

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

        mse.move(rotate_by, 0)
        time.sleep(0.5)

        coods = self.get_coods()
        if coods is None:
            return
        x3, y3, rot3 = coods

        if rot3 > rot2:
            rot3 -= 360

        rot_factor = (rot3 - rot2) / rotate_by
        move_factor = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / walking_time
        self.factors = move_factor, rot_factor
        logging.info(self.factors)

    def on_press(self, key):
        if key == Key.down:
            bot.start = False
            quit()
        elif key == Key.left:
            logging.info(self.get_coods())
        elif key == Key.up:
            self.callibrate()


if __name__ == '__main__':
    logging.getLogger("").setLevel(logging.DEBUG)
    bot = FullAuto(None, None)
    bot.toggle_start()
    with keyboard.Listener(
            on_press=bot.on_press,
    ) as listener:
        listener.join()
