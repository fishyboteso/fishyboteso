import inspect
import logging
import re
import sys
from abc import ABC, abstractmethod
from typing import Tuple, Optional
import platform

from fishy.helper.depless import singleton_proxy


class IOSServices(ABC):

    @abstractmethod
    def hide_terminal(self):
        """
        :return: hides the terminal used to launch fishy
        """

    @abstractmethod
    def create_shortcut(self):
        """
        creates a new shortcut on desktop
        """

    @abstractmethod
    def get_documents_path(self) -> str:
        """
        :return: documents path to save config file
        """

    @abstractmethod
    def is_admin(self) -> bool:
        """
        :return: true if has elevated rights
        """

    @abstractmethod
    def get_eso_config_path(self) -> str:
        """
        :return: path location of the ElderScrollsOnline Folder (in documents) which has "live" folder in it
        """

    @abstractmethod
    def is_eso_active(self) -> bool:
        """
        :return: true if eso is the active window
        """

    @abstractmethod
    def get_monitor_rect(self) -> Optional[Tuple[int, int]]:
        """
        :return: [top, left, height, width] of monitor which has game running in it
        """

    @abstractmethod
    def get_game_window_rect(self) -> Optional[Tuple[int, int, int, int]]:
        """
        :return: location of the game window without any frame
        """


@singleton_proxy("_instance")
class os_services:
    _instance: Optional[IOSServices] = None

    @staticmethod
    def init() -> bool:
        os_name = platform.system()
        if os_name == "Windows":
            from fishy.osservices.windows import Windows
            os_services._instance = Windows()
            return True

        # todo uncomment after linux.py is implemented
        # if os_name == "Linux":
        #     from fishy.osservices.linux import Linux
        #     os_services._instance = Linux()
        #     return True

        return False
