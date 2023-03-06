import logging
from enum import Enum
from threading import Thread

import numpy as np

from mss import mss
from mss.base import MSSBase

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
    sct: MSSBase = None

    crop = None
    monitor_id = -1


def init():
    """
    Executed once before the main loop,
    Finds the game window, and calculates the offset to remove the title bar
    """
    WindowServer.status = Status.RUNNING
    WindowServer.sct = mss()

    WindowServer.crop = os_services.get_game_window_rect()
    monitor_rect = os_services.get_monitor_rect()

    if monitor_rect is None or WindowServer.crop is None:
        logging.error("Game window not found")
        WindowServer.status = Status.CRASHED

    for i, m in enumerate(WindowServer.sct.monitors):
        if m["top"] == monitor_rect[0] and m["left"] == monitor_rect[1]:
            WindowServer.monitor_id = i


def get_cropped_screenshot():
    sct_img = WindowServer.sct.grab(WindowServer.sct.monitors[WindowServer.monitor_id])
    # noinspection PyTypeChecker
    ss = np.array(sct_img)
    crop = WindowServer.crop
    cropped_ss = ss[crop[1]:crop[3], crop[0]:crop[2]]
    if cropped_ss.size == 0:
        return None
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
