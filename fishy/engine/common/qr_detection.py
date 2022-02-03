import cv2
import numpy as np
from pyzbar.pyzbar import decode, ZBarSymbol


def image_pre_process(img):
    scale_percent = 100  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return img


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
            qr_result = decode(og_img[y:h + y, x:w + x],
                               symbols=[ZBarSymbol.QRCODE])
            if qr_result:
                valid_crops.append(((x, y, x + w, y + h), area))

    return min(valid_crops, key=lambda c: c[1])[0] if valid_crops else None


# noinspection PyBroadException
def get_values_from_image(img):
    for qr in decode(img, symbols=[ZBarSymbol.QRCODE]):
        vals = qr.data.decode('utf-8').split(",")
        return tuple(float(v) for v in vals)
    return None
