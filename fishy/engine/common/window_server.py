import logging
from enum import Enum
from threading import Thread

import cv2
import numpy as np
from mss.base import MSSBase

from fishy.engine.common import screenshot
from fishy.helper import helper
from fishy.helper.config import config
from fishy.helper.helper import print_exc
from fishy.osservices.os_services import os_services


class Status(Enum):
    CRASHED = -1
    STOPPED = 0
    RUNNING = 1


class WindowServer:
    """
    Records the game window, and allows to create instance to process it
    """
    Screen: np.ndarray = None
    windowOffset = None
    status = Status.STOPPED
    sslib = None
    crop = None


def init():
    """
    Executed once before the main loop,
    Finds the game window, and calculates the offset to remove the title bar
    """
    WindowServer.sslib = screenshot.create()
    # Check if the screenshot library was successfully created
    if WindowServer.sslib is None:
        logging.error("Failed to create screenshot library instance")
        WindowServer.status = Status.CRASHED
        return

    crop = os_services.get_game_window_rect()
    if crop is None or not WindowServer.sslib.setup():
        logging.error("Game window not found by window_server")
        WindowServer.status = Status.CRASHED
        return

    WindowServer.crop = crop
    WindowServer.status = Status.RUNNING


def get_cropped_screenshot():
    ss = WindowServer.sslib.grab()

    if config.get("show_grab", 0):
        helper.save_img("full screen", ss)

    crop = WindowServer.crop
    cropped_ss = ss[crop[1]:crop[3], crop[0]:crop[2]]

    if cropped_ss.size == 0:
        return None

    if config.get("show_grab", 0):
        helper.save_img("Game window", cropped_ss)

    return cropped_ss


def loop():
    """
    Executed in the start of the main loop
    finds the game window location and captures it
    """
    WindowServer.Screen = get_cropped_screenshot()

    if WindowServer.Screen is None:
        logging.error("Couldn't find the game window")
        WindowServer.status = Status.CRASHED


# noinspection PyBroadException
def run():
    # todo use config
    logging.debug("window server started")
    while WindowServer.status == Status.RUNNING:
        try:
            loop()
        except Exception:
            print_exc()
            WindowServer.status = Status.CRASHED

    if WindowServer.status == Status.CRASHED:
        logging.debug("window server crashed")
    elif WindowServer.status == Status.STOPPED:
        logging.debug("window server stopped")


def start():
    if WindowServer.status == Status.RUNNING:
        return

    init()
    if WindowServer.status == Status.RUNNING:
        Thread(target=run).start()


def screen_ready():
    return WindowServer.Screen is not None or WindowServer.status == Status.CRASHED


def stop():
    WindowServer.status = Status.STOPPED
