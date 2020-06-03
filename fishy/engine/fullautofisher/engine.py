import cv2
import logging
import time

import numpy as np
import pywintypes

from fishy.engine.IEngine import IEngine
from fishy.engine.window import Window


class FullAuto(IEngine):
    def run(self):

        try:
            Window.init(False)
        except pywintypes.error:
            logging.info("Game window not found")
            self.start = False
            return

        self.window = Window(color=cv2.COLOR_RGB2GRAY)

        if self.get_gui is not None:
            self.gui.bot_started(True)
        while self.start:
            Window.loop()

            img = self.window.get_capture()
            img = cv2.inRange(img, 0, 1)
            cnt, h = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            """
            code from https://stackoverflow.com/a/45770227/4512396
            """
            crop = self.window.get_capture()
            for i in range(len(cnt)):
                area = cv2.contourArea(cnt[i])
                if 5000 < area < 100000:
                    mask = np.zeros_like(img)
                    cv2.drawContours(mask, cnt, i, 255, -1)
                    x, y, w, h = cv2.boundingRect(cnt[i])
                    crop = self.window.get_capture()[y:h + y, x:w + x]

            # cnt, h = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # print(cnt)

            self.window.show("test", ready_img=crop)
            Window.loop_end()
        self.gui.bot_started(False)


if __name__ == '__main__':
    bot = FullAuto(None, None)
    bot.toggle_start()
