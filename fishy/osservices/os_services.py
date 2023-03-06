import inspect
import logging
import re
import sys
from abc import ABC, abstractmethod
from typing import Tuple, Optional
import platform


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
    def get_monitor_rect(self):
        """
        :return: [top, left, height, width] of monitor which has game running in it
        """

    @abstractmethod
    def get_game_window_rect(self) -> Optional[Tuple[int, int, int, int]]:
        """
        :return: location of the game window without any frame
        """


# todo move this into helper and use for config and similar places
# but make sure other fishy stuff is not imported while importing helper
# to do that, move everything which uses fishy stuff into a different helper script
def singleton_proxy(instance_name):
    def decorator(root_cls):
        if not hasattr(root_cls, instance_name):
            raise AttributeError(f"{instance_name} not found in {root_cls}")

        class SingletonProxy(type):
            def __getattr__(cls, name):
                return getattr(getattr(cls, instance_name), name)

        class NewClass(root_cls, metaclass=SingletonProxy):
            ...

        return NewClass

    return decorator


@singleton_proxy("_instance")
class os_services:
    _instance: Optional[IOSServices] = None

    @staticmethod
    def init():
        os_name = platform.system()
        if os_name == "Windows":
            from fishy.osservices.windows import Windows
            os_services._instance = Windows()
        elif os_name == "Linux":
            from fishy.osservices.linux import Linux
            os_services._instance = Linux()
        else:
            logging.error("Platform not supported")
