import sys
from decimal import Decimal

import cv2
import numpy as np


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
