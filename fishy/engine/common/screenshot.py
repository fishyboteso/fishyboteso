import logging
import subprocess
import traceback
from abc import ABC, abstractmethod
from functools import partial
from typing import Optional

import numpy as np
from numpy import ndarray

from fishy import constants
from fishy.helper.config import config
from fishy.osservices.os_services import os_services


class IScreenShot(ABC):
    @abstractmethod
    def setup(self) -> bool:
        ...

    @abstractmethod
    def grab(self) -> ndarray:
        ...


def get_monitor_id(monitors_iterator, get_top_left) -> Optional[int]:
    monitor_rect = os_services.get_monitor_rect()
    if monitor_rect is None:
        logging.error("Game window not found")
        return None

    for i, m in enumerate(monitors_iterator):
        top, left = get_top_left(m)
        if top == monitor_rect[1] and left == monitor_rect[0]:
            return i

    return None


class MSS(IScreenShot):
    def __init__(self):
        from mss import mss
        self.monitor_id = None
        self.sct = mss()

    def setup(self) -> bool:
        self.monitor_id = get_monitor_id(self.sct.monitors, lambda m: (m["top"], m["left"]))
        return self.monitor_id is not None

    # noinspection PyTypeChecker
    def grab(self) -> ndarray:
        sct_img = self.sct.grab(self.sct.monitors[self.monitor_id])
        return np.array(sct_img)


class PyAutoGUI(IScreenShot):
    def __init__(self):
        self.monitor_rect = None

    def setup(self) -> bool:
        from PIL import ImageGrab
        ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
        self.monitor_rect = os_services.get_monitor_rect()
        return True

    def grab(self) -> ndarray:
        import pyautogui
        image = pyautogui.screenshot()
        img = np.array(image)
        crop = self.monitor_rect
        img = img[crop[1]:crop[3], crop[0]:crop[2]]
        return img


class D3DShot(IScreenShot):
    # noinspection PyPackageRequirements
    def __init__(self):
        try:
            import d3dshot
        except ImportError:
            logging.info("Installing d3dshot please wait...")
            subprocess.call(["python", "-m", "pip", "install", constants.d3dshot_git])
            import d3dshot

        self.d3 = d3dshot.create(capture_output="numpy")

    def setup(self) -> bool:
        monitor_id = get_monitor_id(self.d3.displays, lambda m: (m.position["top"], m.position["left"]))
        if monitor_id is None:
            return False

        self.d3.display = self.d3.displays[monitor_id]
        return True

    def grab(self) -> ndarray:
        return self.d3.screenshot()


LIBS = [PyAutoGUI, MSS, D3DShot]


# noinspection PyBroadException
def create() -> Optional[IScreenShot]:
    # Initialize a variable to hold the preferred library index
    preferred_lib_index = config.get("sslib", 0)
    # Create a list of library indices to try, starting with the preferred one
    lib_indices = [preferred_lib_index] + [i for i in range(len(LIBS)) if i != preferred_lib_index]

    for index in lib_indices:
        lib = LIBS[index]
        try:
            lib_instance = lib()
            if lib_instance.setup():
                # testing grab once
                ss = lib_instance.grab()
                if ss.shape:
                    logging.debug(f"Using {lib.__name__} as the screenshot library.")
                    return lib_instance
        except Exception:
            logging.warning(f"Setup failed for {lib.__name__} with error: {traceback.format_exc()}. Trying next library...")

    return None
