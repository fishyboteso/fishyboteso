import logging
import math
from enum import Enum
from threading import Thread

import numpy as np
import pywintypes
import win32api
import win32gui
from ctypes import windll

from mss import mss
from mss.base import MSSBase

from fishy.helper.helper import print_exc


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
    hwnd = None
    status = Status.STOPPED
    sct: MSSBase = None
    monitor_top_left = None


def init():
    """
    Executed once before the main loop,
    Finds the game window, and calculates the offset to remove the title bar
    """
    # noinspection PyUnresolvedReferences
    try:
        WindowServer.hwnd = win32gui.FindWindow(None, "Elder Scrolls Online")

        monitor_id = windll.user32.MonitorFromWindow(WindowServer.hwnd, 2)
        WindowServer.monitor_top_left = win32api.GetMonitorInfo(monitor_id)["Monitor"][:2]

        rect = win32gui.GetWindowRect(WindowServer.hwnd)
        client_rect = win32gui.GetClientRect(WindowServer.hwnd)
        WindowServer.windowOffset = math.floor(((rect[2] - rect[0]) - client_rect[2]) / 2)
        WindowServer.status = Status.RUNNING
        WindowServer.sct = mss()

    except pywintypes.error:
        logging.error("Game window not found")
        WindowServer.status = Status.CRASHED


def loop():
    """
    Executed in the start of the main loop
    finds the game window location and captures it
    """

    sct_img = WindowServer.sct.grab(WindowServer.sct.monitors[1])
    # noinspection PyTypeChecker
    temp_screen = np.array(sct_img)

    rect = win32gui.GetWindowRect(WindowServer.hwnd)
    client_rect = win32gui.GetClientRect(WindowServer.hwnd)

    fullscreen = sct_img.size.height == (rect[3] - rect[1])
    title_offset = ((rect[3] - rect[1]) - client_rect[3]) - WindowServer.windowOffset if not fullscreen else 0
    crop = (
        rect[0] + WindowServer.windowOffset - WindowServer.monitor_top_left[0],
        rect[1] + title_offset - WindowServer.monitor_top_left[1],
        rect[2] - WindowServer.windowOffset - WindowServer.monitor_top_left[0],
        rect[3] - WindowServer.windowOffset - WindowServer.monitor_top_left[1]
    )

    WindowServer.Screen = temp_screen[crop[1]:crop[3], crop[0]:crop[2]] if not fullscreen else temp_screen

    if WindowServer.Screen.size == 0:
        logging.error("Don't minimize or drag game window outside the screen")
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
