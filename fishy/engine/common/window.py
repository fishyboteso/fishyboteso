import logging
import uuid
from typing import List

import cv2
import imutils

from fishy.engine.common import window_server
from fishy.engine.common.window_server import Status, WindowServer
from fishy.helper import helper
from fishy.helper.config import config


class WindowClient:
    clients: List['WindowClient'] = []

    def __init__(self):
        """
        create a window instance with these pre process
        :param crop: [x1,y1,x2,y2] array defining the boundaries to crop
        :param color: color to use example cv2.COLOR_RGB2HSV
        :param scale: scaling the window
        """
        self.crop = None
        self.scale = None
        self.show_name = f"window client {len(WindowClient.clients)}"

        WindowClient.clients.append(self)
        if len(WindowClient.clients) > 0 and WindowServer.status != Status.RUNNING:
            window_server.start()

    @staticmethod
    def running():
        return WindowServer.status == Status.RUNNING

    def processed_image(self, func=None):
        """
        processes the image using the function provided
        :param func: function to process image
        :return: processed image
        """
        if WindowServer.status == Status.CRASHED:
            return None

        img = self._get_capture()

        if img is None:
            return None

        if func:
            img = func(img)

        if config.get("show_grab", 0):
            self._show(img)

        return img

    def destroy(self):
        if self in WindowClient.clients:
            WindowClient.clients.remove(self)
        if len(WindowClient.clients) == 0:
            window_server.stop()

    def _get_capture(self):
        """
        copies the recorded screen and then pre processes its
        :return: game window image
        """
        if WindowServer.status == Status.CRASHED:
            return None

        if not window_server.screen_ready():
            logging.debug("waiting for screen...")
            helper.wait_until(window_server.screen_ready)
            logging.debug("screen ready, continuing...")

        temp_img = WindowServer.Screen

        if temp_img is None or temp_img.size == 0:
            return None

        temp_img = cv2.cvtColor(temp_img, cv2.COLOR_RGB2GRAY)

        if self.crop is not None:
            temp_img = temp_img[self.crop[1]:self.crop[3], self.crop[0]:self.crop[2]]

        if self.scale is not None:
            temp_img = cv2.resize(temp_img, (self.scale[0], self.scale[1]), interpolation=cv2.INTER_AREA)

        # need ot check again after crop/resize
        if temp_img.size == 0:
            return None

        return temp_img

    # noinspection PyUnresolvedReferences
    def _show(self, img):
        """
        Displays the processed image for debugging purposes
        """
        if WindowServer.status == Status.CRASHED:
            return

        helper.save_img(self.show_name, img, True)
