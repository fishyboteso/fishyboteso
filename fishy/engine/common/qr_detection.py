import logging
import re

import cv2
import numpy as np

detector = cv2.QRCodeDetector()


def image_pre_process(img):
    scale_percent = 100  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return img


def get_qr_location(image):
    """
    code from https://stackoverflow.com/a/45770227/4512396
    """
    success, points = detector.detect(image)
    if not success:
        return None

    p = points[0]
    # (x, y, x + w, y + h)
    return [int(x) for x in [p[0][0], p[0][1], p[1][0], p[2][1]]]


# noinspection PyBroadException
def get_values_from_image(img):
    h, w = img.shape
    points = np.array([[(0, 0), (w, 0), (w, h), (0, h)]])
    code = detector.decode(img, points)[0]
    return parse_qr_code(code)


# this needs to be updated each time qr code format is changed
def parse_qr_code(code):
    if not code:
        return None
    match = re.match(r'^(\d+\.\d+),(\d+\.\d+),(\d+),(\d+)$', code)
    if not match:
        logging.warning(f"qr code is not what was expected {code}")
        return None
    return [float(match.group(1)), float(match.group(2)), int(match.group(3)), int(match.group(4))]
