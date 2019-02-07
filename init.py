"""Fishy

Usage:
  fishy.py -h | --help
  fishy.py -v | --version
  fishy.py [--ip=<ipv4>] [--hook-threshold=<int>] [--check-frequency=<hz>] [--no-resize]

Options:
  -h, --help                Show this screen.
  -v, --version             Show version.
  --ip=<ipv4>               Local Ip Address of the android phone.
  --hook-threshold=<int>    Threshold amount for classifier after which label changes [default: 3].
  --check-frequency=<hz>    Sleep after loop in s [default: 10].
"""

VERSION = "0.1.0"
print("Fishy " + VERSION + " for Elder Scrolls Online")

try:
    from docopt import docopt

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
    import fishy_network as net
    from fishy_config import config_win
    from pynput.keyboard import Key, Listener
    from decimal import Decimal
    from win32api import GetSystemMetrics
    import pickle
    import win32gui
    from abc import ABC, abstractmethod
except Exception:
    raise


class G:
    fishCaught = 0
    stickInitTime = 0
    controls = {"stop": [Key.f11, "f11"], "debug": [Key.f10, "f10"], "pause": [Key.f9, "f9"],
                "configPL": [Key.f8, "f8"]}
    stop = False
    pause = True
    debug = False
    configPL = False


class Log:
    ouUsed = False
    prevOuUsed = False
    ctrl_help = G.controls["configPL"][1] + ": config pixel value\n" + G.controls["pause"][1] + ": start or pause\n" + \
                G.controls["debug"][1] + ": start debug\n" + G.controls["stop"][1] + ": quit\n"

    @staticmethod
    def Loop():
        Log.ouUsed = False

    @staticmethod
    def LoopEnd():
        if Log.prevOuUsed and not Log.ouUsed:
            print(Log.ctrl_help)
        Log.prevOuUsed = Log.ouUsed

    @staticmethod
    def ctrl():
        print(Log.ctrl_help)

    @staticmethod
    def ou(s):
        Log.ouUsed = True
        print(s)


def round_float(v, ndigits=2, rt_str=False):
    d = Decimal(v)
    v_str = ("{0:.%sf}" % ndigits).format(round(d, ndigits))
    if rt_str:
        return v_str
    return Decimal(v_str)
