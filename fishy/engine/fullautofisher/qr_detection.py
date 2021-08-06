import logging
import os
from datetime import datetime

import cv2
import numpy as np
from pyzbar.pyzbar import decode

from fishy.helper.helper import get_documents

# temp fix for qr loss
from pynput import mouse 

def get_qr_location(og_img):
    """
    code from https://stackoverflow.com/a/45770227/4512396
    """
    gray = cv2.bilateralFilter(og_img, 11, 17, 17)
    kernel = np.ones((5, 5), np.uint8)
    erosion = cv2.erode(gray, kernel, iterations=2)
    kernel = np.ones((4, 4), np.uint8)
    img = cv2.dilate(erosion, kernel, iterations=2)

    cnt, h = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    valid_crops = []
    for i in range(len(cnt)):
        area = cv2.contourArea(cnt[i])
        if 500 < area < 100000:
            mask = np.zeros_like(img)
            cv2.drawContours(mask, cnt, i, 255, -1)
            x, y, w, h = cv2.boundingRect(cnt[i])
            qr_result = decode(og_img[y:h + y, x:w + x])
            if qr_result:
                valid_crops.append(((x, y, x + w, y + h), area))

    return min(valid_crops, key=lambda c: c[1])[0] if valid_crops else None


# noinspection PyBroadException
def get_values_from_image(img):
    retry_counter = 0
    try:
        for qr in decode(img):
            vals = qr.data.decode('utf-8').split(",")
            if not vals:
                if retry_counter < 5:
                    logging.error("FishyQR not found, wiggling mouse")
                    mmover = mouse.Controller()
                    mmover.move(0, -FullAuto.rotate_by)
                    time.sleep(0.05)
                    self._curr_rotate_y -= 0.05
                    retry_counter += 1
                else:
                    return None
            else:
                return float(vals[0]), float(vals[1]), float(vals[2])

    except Exception:
        logging.error("Couldn't read coods, make sure 'crop' calibration is correct")
        cv2.imwrite(os.path.join(get_documents(), "fishy_failed_reads", f"{datetime.now()}.jpg"), img)
        return None
