import logging
from tkinter import OptionMenu, Button
from typing import List, Callable, Optional
import threading

from ttkthemes import ThemedTk

from fishy.engine.common.event_handler import EngineEventHandler
from fishy.gui import config_top
from fishy.gui.funcs import GUIFuncs
from . import main_gui
from .log_config import GUIStreamHandler
from ..helper.config import config


class GUI:
    def __init__(self, get_engine: Callable[[], EngineEventHandler]):
        self.funcs = GUIFuncs(self)
        self.get_engine = get_engine

        self.config = config
        self._start_restart = False
        self._destroyed = True
        self._log_strings = []
        self._function_queue: List[Callable] = []
        self._bot_running = False

        # UI items
        self._root: Optional[ThemedTk] = None
        self._console = None
        self._start_button = None
        self._notify = None
        self._notify_check = None
        self._engine_select: Optional[OptionMenu] = None
        self._config_button: Optional[Button] = None
        self._engine_var = None

        self._thread = threading.Thread(target=self.create, args=())

        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        new_console = GUIStreamHandler(self)
        root_logger.addHandler(new_console)

    @property
    def engine(self):
        return self.get_engine()

    @property
    def engines(self):
        engines = {
            "Semi Fisher": [lambda: config_top.start_semifisher_config(self), self.engine.toggle_semifisher],
        }

        if config.get('debug', False):
            engines["Full-Auto Fisher"] = [lambda: config_top.start_fullfisher_config(self),
                                           self.engine.toggle_fullfisher]
        return engines

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
