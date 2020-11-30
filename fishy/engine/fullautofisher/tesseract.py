import logging
import os
import tempfile
import uuid
from datetime import datetime
from zipfile import ZipFile

import cv2

import pytesseract

from fishy.helper.downloader import download_file_from_google_drive
from fishy.helper.helper import get_documents

directory = os.path.join(os.environ["APPDATA"], "Tesseract-OCR")


def downlaoad_and_extract_tesseract():
    logging.info("Tesseract-OCR downlaoding, Please wait...")

    f = tempfile.NamedTemporaryFile(delete=False)
    download_file_from_google_drive("16llzcBlaCsG9fm-rY2dD4Gvopnhm3XoE", f)
    f.close()

    logging.info("Tesseract-OCR downloaded, now installing")

    with ZipFile(f.name, 'r') as z:
        z.extractall(path=directory)

    logging.info("Tesseract-OCR installed")


def is_tesseract_installed():
    return os.path.exists(os.path.join(os.environ["APPDATA"], "Tesseract-OCR"))


# noinspection PyBroadException
def get_values_from_image(img):
    try:
        pytesseract.pytesseract.tesseract_cmd = directory + '/tesseract.exe'
        tessdata_dir_config = f'--tessdata-dir "{directory}" -c tessedit_char_whitelist=0123456789.'

        text = pytesseract.image_to_string(img, lang="eng", config=tessdata_dir_config)
        text = text.replace(" ", "")
        vals = text.split(":")
        return float(vals[0]), float(vals[1]), float(vals[2])
    except Exception:
        logging.error("Couldn't read coods, make sure 'crop' calibration is correct")
        cv2.imwrite(os.path.join(get_documents(), "fishy_failed_reads", f"{datetime.now()}.jpg"), img)
        return None
