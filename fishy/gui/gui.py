import logging
from typing import Tuple, List, Callable, Optional
import threading

from . import main_gui
from .comms import GUIEvent, GUIFunction
from .log_config import GUIStreamHandler
from fishy.helper import Config


class GUI:
    def __init__(self, config: Config, event_trigger: Callable[[GUIEvent, Optional[Tuple]], None]):
        """
        :param config: used to get and set configuration settings
        :param event_trigger: used to communicate with other threads
        """
        self._config = config
        self._start_restart = False
        self._destroyed = True
        self._log_strings = []
        self._function_queue: List[Tuple[GUIFunction, Tuple]] = []
        self._event_trigger = event_trigger
        self._bot_running = False

        # UI items
        self._root = None
        self._console = None
        self._start_button = None
        self._notify = None
        self._notify_check = None

        self._thread = threading.Thread(target=self.create, args=())

        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        new_console = GUIStreamHandler(self)
        root_logger.addHandler(new_console)

    def create(self):
        main_gui._create(self)

    def start(self):
        self._thread.start()

    def call(self, gui_func, args):
        self._function_queue.append((gui_func, args))
