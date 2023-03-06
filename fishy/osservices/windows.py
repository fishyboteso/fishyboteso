import ctypes
import logging
import math
import os
import sys
from typing import Tuple, Optional

import pywintypes
import win32api
import win32con
import win32gui
import winshell
from win32com.client import Dispatch
from win32comext.shell import shell, shellcon
from win32gui import GetForegroundWindow, GetWindowText


from ctypes import windll

from fishy.helper import manifest_file
from fishy.osservices.os_services import IOSServices


def _check_window_name(title):
    titles = ["Command Prompt", "PowerShell", "Fishy"]
    for t in titles:
        if t in title:
            return True
    return False


class Windows(IOSServices):
    def is_admin(self) -> bool:
        try:
            is_admin = os.getuid() == 0
        except AttributeError:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        return is_admin

    def is_eso_active(self) -> bool:
        return GetWindowText(GetForegroundWindow()) == "Elder Scrolls Online"

    # noinspection PyBroadException
    def create_shortcut(self, anti_ghosting=False):
        try:
            desktop = winshell.desktop()
            path = os.path.join(desktop, "Fishybot ESO.lnk")
            _shell = Dispatch('WScript.Shell')
            shortcut = _shell.CreateShortCut(path)

            if anti_ghosting:
                shortcut.TargetPath = r"C:\Windows\System32\cmd.exe"
                python_dir = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
                shortcut.Arguments = f"/C start /affinity 1 /low {python_dir} -m fishy"
            else:
                shortcut.TargetPath = os.path.join(os.path.dirname(sys.executable), "python.exe")
                shortcut.Arguments = "-m fishy"

            shortcut.IconLocation = manifest_file("icon.ico")
            shortcut.save()

            logging.info("Shortcut created")
        except Exception:
            logging.error("Couldn't create shortcut")

    def __init__(self):
        self.to_hide = win32gui.GetForegroundWindow()

    def hide_terminal(self):
        if _check_window_name(win32gui.GetWindowText(self.to_hide)):
            win32gui.ShowWindow(self.to_hide, win32con.SW_HIDE)

    def get_documents_path(self) -> str:
        return shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)

    def get_eso_config_path(self) -> str:
        # noinspection PyUnresolvedReferences
        from win32com.shell import shell, shellcon
        documents = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
        return os.path.join(documents, "Elder Scrolls Online")

    def get_monitor_rect(self):
        # noinspection PyUnresolvedReferences
        try:
            hwnd = win32gui.FindWindow(None, "Elder Scrolls Online")
            monitor = windll.user32.MonitorFromWindow(hwnd, 2)
            monitor_info = win32api.GetMonitorInfo(monitor)
            return monitor_info["Monitor"]
        except pywintypes.error:
            return None

    def get_game_window_rect(self) -> Optional[Tuple[int, int, int, int]]:
        hwnd = win32gui.FindWindow(None, "Elder Scrolls Online")
        monitor_rect = self.get_monitor_rect()

        # noinspection PyUnresolvedReferences
        try:
            rect = win32gui.GetWindowRect(hwnd)
            client_rect = win32gui.GetClientRect(hwnd)
            windowOffset = math.floor(((rect[2] - rect[0]) - client_rect[2]) / 2)
            fullscreen = monitor_rect[3] == (rect[3] - rect[1])
            title_offset = ((rect[3] - rect[1]) - client_rect[3]) - windowOffset if not fullscreen else 0

            game_rect = (
                rect[0] + windowOffset - monitor_rect[0],
                rect[1] + title_offset - monitor_rect[1],
                rect[2] - windowOffset - monitor_rect[0],
                rect[3] - windowOffset - monitor_rect[1]
            )
            return game_rect
        except pywintypes.error:
            return None
