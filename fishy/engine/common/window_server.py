import logging
from enum import Enum
from threading import Thread

import cv2
import math
import time

import pywintypes
from win32api import GetSystemMetrics
from win32gui import GetWindowRect, FindWindow, GetClientRect

import numpy as np
from PIL import ImageGrab

from fishy.helper.config import config


class Status(Enum):
    CRASHED = -1
    STOPPED = 0
    RUNNING = 1


class WindowServer:
    """
    Records the game window, and allows to create instance to process it
    """
    windowOffset = None
    titleOffset = None
    hwnd = None
    status = Status.STOPPED
    qrCodeDetector = cv2.QRCodeDetector()
    qrcontent = None


def init():
    """
    Executed once before the main loop,
    Finds the game window, and calculates the offset to remove the title bar
    """
    try:
        WindowServer.hwnd = FindWindow(None, "Elder Scrolls Online")
        rect = GetWindowRect(WindowServer.hwnd)
        client_rect = GetClientRect(WindowServer.hwnd)
        WindowServer.windowOffset = math.floor(((rect[2] - rect[0]) - client_rect[2]) / 2)
        WindowServer.titleOffset = ((rect[3] - rect[1]) - client_rect[3]) - WindowServer.windowOffset
        if config.get("borderless"):
            WindowServer.titleOffset = 0
        WindowServer.status = Status.RUNNING
    except pywintypes.error:
        logging.error("Game window not found")
        WindowServer.status = Status.CRASHED


def loop():
    """
    Executed in the start of the main loop
    finds the game window location and captures it
    """
    try:
        window = GetWindowRect(FindWindow(None, "Elder Scrolls Online"))
        """
        TODO: crop to magic number
        cropping first speeds up the process enormous
        """
        mgk_num = 4
        windowcrop = (window[0],window[1],int(window[2]/mgk_num),int(window[3]/mgk_num))
        temp_img = np.array(ImageGrab.grab(bbox=windowcrop))
    except OSError:
        logging.error("ImageGrab failed")
        WindowServer.qrcontent = None
        time.sleep(0.5)
        return
    except:
        logging.error("ESO not started")
        WindowServer.status = Status.CRASHED

    if temp_img.size == 0:
        logging.error("Don't minimize or drag game window outside the screen")
        WindowServer.qrcontent = None
        time.sleep(0.5)
        return

    #color does not matter
    temp_img = cv2.cvtColor(temp_img, cv2.COLOR_BGR2RGB)

    decodedText, points, _ = WindowServer.qrCodeDetector.detectAndDecode(temp_img)

    if points is None:
        WindowServer.qrcontent = None
        time.sleep(0.5)
        return
    elif decodedText == "stop" or decodedText == "" :
        #reduce polling when stopped or invalid
        WindowServer.qrcontent = None
        time.sleep(0.5)
        return

    WindowServer.qrcontent = decodedText.split(",")


def loop_end():
    cv2.waitKey(25)


def run():
    # todo use config
    while WindowServer.status == Status.RUNNING:
        loop()
    loop_end()


def start():
    if WindowServer.status == Status.RUNNING:
        return

    init()
    if WindowServer.status == Status.RUNNING:
        Thread(target=run).start()


def qrcontent_ready():
    return WindowServer.qrcontent is not None or WindowServer.status == Status.CRASHED


def stop():
    WindowServer.status = Status.STOPPED
