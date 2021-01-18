import logging
from typing import List

import cv2
import imutils

from fishy.engine.common import window_server
from fishy.engine.common.window_server import WindowServer, Status
from fishy.helper import helper


class WindowClient:
    clients: List['WindowClient'] = []

    def __init__(self, crop=None, color=None, scale=None, show_name=None):
        """
        create a window instance with these pre process
        :param crop: [x1,y1,x2,y2] array defining the boundaries to crop
        :param color: color to use example cv2.COLOR_RGB2HSV
        :param scale: scaling the window
        """
        self.color = color
        self.crop = crop
        self.scale = scale
        self.show_name = show_name

        if len(WindowClient.clients) == 0:
            window_server.start()
        WindowClient.clients.append(self)

    def destory(self):
        if self in WindowClient.clients:
            WindowClient.clients.remove(self)
        if len(WindowClient.clients) == 0:
            window_server.stop()
            logging.info("window server stopped")

    @staticmethod
    def running():
        return WindowServer.status == Status.RUNNING


    def get_qrcontent(self):
        if WindowServer.status == Status.CRASHED:
            return None

        if not window_server.qrcontent_ready():
            print("waiting for qrcontent...")
            helper.wait_until(window_server.qrcontent_ready)
            print("qrcontent ready, continuing...")

        return WindowServer.qrcontent
