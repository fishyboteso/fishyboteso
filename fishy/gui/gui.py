import logging
from typing import List, Callable
import threading

from ttkthemes import ThemedTk

from fishy.engine.event_handler import EngineEventHandler
from fishy.gui.funcs import GUIFuncs
from . import main_gui
from .log_config import GUIStreamHandler
from fishy.helper import Config


class GUI:
    def __init__(self, config: Config, get_engine: Callable[[], EngineEventHandler]):
        """
        :param config: used to get and set configuration settings
        """
        self.funcs = GUIFuncs(self)
        self.get_engine = get_engine

        self._config = config
        self._start_restart = False
        self._destroyed = True
        self._log_strings = []
        self._function_queue: List[Callable] = []
        self._bot_running = False

        # UI items
        self._root: ThemedTk = None
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

    @property
    def engine(self):
        return self.get_engine()

    def create(self):
        main_gui._create(self)

    def start(self):
        self._thread.start()

    def _clear_function_queue(self):
        while len(self._function_queue) > 0:
            func = self._function_queue.pop(0)
            func()

    def call_in_thread(self, func: Callable):
        self._function_queue.append(func)

    def _get_start_stop_text(self):
        return "STOP (F9)" if self._bot_running else "START (F9)"
