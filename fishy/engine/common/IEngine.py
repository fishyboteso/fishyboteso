import logging
import traceback
import typing
from threading import Thread
from typing import Callable

from playsound import playsound

from fishy.gui.funcs import GUIFuncsMock
from fishy.helper import helper

if typing.TYPE_CHECKING:
    from fishy.gui import GUI


class IEngine:

    def __init__(self, gui_ref: 'Callable[[], GUI]'):
        self.get_gui = gui_ref
        # 0 - off, 1 - running, 2 - quitting
        self.state = 0
        self.window = None
        self.thread = None

    @property
    def gui(self):
        if self.get_gui is None:
            return GUIFuncsMock()

        return self.get_gui().funcs

    def toggle_start(self):
        if self.state == 1:
            self.turn_off()
        elif self.state == 0:
            self.turn_on()

    def turn_on(self):
        self.state = 1
        playsound(helper.manifest_file("beep.wav"), False)
        self.thread = Thread(target=self._crash_safe)
        self.thread.start()

    def turn_off(self):
        """
        this method only signals the thread to close using start flag,
        its the responsibility of the thread to shut turn itself off
        """
        self.state = 2
        helper.playsound_multiple(helper.manifest_file("beep.wav"))

    # noinspection PyBroadException
    def _crash_safe(self):
        self.gui.bot_started(True)
        try:
            self.run()
        except Exception:
            traceback.print_exc()
        self.state = 0
        self.gui.bot_started(False)

    def run(self):
        raise NotImplementedError
