import logging
import re

import cv2
import numpy as np
from fishy.engine.common.window import WindowClient

detector = cv2.QRCodeDetector()


# noinspection PyBroadException
def get_values(window: WindowClient):
    values = None
    for _ in range(6):
        img = window.processed_image()
        if img is None:
            logging.debug("Couldn't capture window.")
            continue

        if not window.crop:
            window.crop = _get_qr_location(img)
            if not window.crop:
                logging.debug("FishyQR not found.")
            continue

        values = _get_values_from_image(img)
        if not values:
            window.crop = None
            logging.debug("Values not able to read.")
            continue
        break

    return values


def _get_qr_location(image):
    """
    code from https://stackoverflow.com/a/45770227/4512396
    """
    success, points = detector.detect(image)
    if not success:
        return None

    p = points[0]
    # (x, y, x + w, y + h)
    return [int(x) for x in [p[0][0], p[0][1], p[1][0], p[2][1]]]


def _get_values_from_image(img):
    h, w = img.shape
    points = np.array([[(0, 0), (w, 0), (w, h), (0, h)]])
    code = detector.decode(img, points)[0]
    return _parse_qr_code(code)


def _brute_cast(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return None


def _parse_qr_code(code):
    if not code:
        return None
    strings = code.split(",")
    # this needs to be updated if qr code contains additional data
    values = [_brute_cast(value) for value in strings][0:4]
    
    if None in values
        logging.warning(f"qr code is not what was expected {code}")
        return None

    return values
