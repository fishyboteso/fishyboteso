"""Fishy

Usage:
  fishy.py -h | --help
  fishy.py -v | --version
  fishy.py [--debug] [--ip=<ipv4>] [--hook-threshold=<int>] [--check-frequency=<hz>] [--collect-r] [--borderless]

Options:
  -h, --help                Show this screen.
  -v, --version             Show version.
  --ip=<ipv4>               Local Ip Address of the android phone.
  --hook-threshold=<int>    Threshold amount for classifier after which label changes [default: 1].
  --check-frequency=<hz>    Sleep after loop in s [default: 1].
  --debug                   Start program in debug controls.
  --borderless              Use if the game is in fullscreen or borderless window
"""

VERSION = "0.1.3"
print("Fishy " + VERSION + " for Elder Scrolls Online")

try:
    from docopt import docopt

    # docopt checks if cli args are correct, if its not, it shows the correct syntax and quits
    arguments = docopt(__doc__)
    if arguments["--version"]:
        quit()

    print("Loading, Please Wait...")
    import imutils as imutils
    import numpy as np
    from PIL import ImageGrab
    import cv2
    import pyautogui
    import time
    from systems import fishy_network as net
    from pynput.keyboard import Key, Listener
    from decimal import Decimal
    from win32api import GetSystemMetrics
    import pickle
    import win32gui
    import pywintypes
    from abc import ABC, abstractmethod
    from enum import Enum
    import sys
    import numpy as np
    import math
    import os
    import re
except Exception:
    print("Modules not installed properly, try running `pip install -r requirements.txt`")
    raise

'''
import stack
shows the sequence of execution of each python scripts (bottom to up)
scripts which are higher on the stack depends on the scripts below them
script which is on top is called which then imports ones below it
each scrip creates different services which is then used inside `fishy.py script

fishy               Reads input and uses `controls.py` to execute different commands
                    Contains the main loop of the bot, 
                    calls different services and helps them to communicate to each other
pixel_loc           finds the location of the pixel which is used to detect different states (called PixelLoc)
fishing_event       implements different states along with their callbacks (idle, stick, hooked, look)
fishing_mode        state machine for different fishing mode 
window              recodes the game window, and gives method to process them
log                 very simple logging functions
controls            creates an input system for the bot
init                initializes global variables and imports all the libraries
'''


class G:
    """
    Initialize global variables used by different services
    """
    fishCaught = 0
    totalFishCaught = 0
    stickInitTime = 0
    stop = False
    pause = True
    debug = False


"""Helper functions"""


def round_float(v, ndigits=2, rt_str=False):
    """
    Rounds float
    :param v: float ot round off
    :param ndigits: round off to ndigits decimal points
    :param rt_str: true to return string
    :return: rounded float or strings
    """
    d = Decimal(v)
    v_str = ("{0:.%sf}" % ndigits).format(round(d, ndigits))
    if rt_str:
        return v_str
    return Decimal(v_str)


def draw_keypoints(vis, keypoints, color=(0, 0, 255)):
    """
    draws a point on cv2 image array
    :param vis: cv2 image array to draw
    :param keypoints: keypoints array to draw
    :param color: color of the point
    """
    for kp in keypoints:
        x, y = kp.pt
        cv2.circle(vis, (int(x), int(y)), 5, color, -1)

def enable_full_array_printing():
    """
    Used to enable full array logging
    (summarized arrays are printed by default)
    """
    np.set_printoptions(threshold=sys.maxsize)
