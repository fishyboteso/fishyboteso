import logging
import subprocess
from abc import ABC, abstractmethod
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
        if top == monitor_rect[0] and left == monitor_rect[1]:
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
    def setup(self) -> bool:
        return True

    def grab(self) -> ndarray:
        import pyautogui
        image = pyautogui.screenshot(all_screens=True)
        return np.array(image)


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


LIBS = [MSS, PyAutoGUI, D3DShot]


def create() -> IScreenShot:
    return LIBS[config.get("sslib", 0)]()
