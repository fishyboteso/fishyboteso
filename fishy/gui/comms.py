import threading
from enum import Enum
from tkinter import *
from tkinter import messagebox, filedialog

from .log_config import _write_to_console
import typing

if typing.TYPE_CHECKING:
    from . import GUI


class GUIEvent(Enum):
    START_BUTTON = 0  # args: ip: str, action_key: str, fullscreen: bool, collect_r: bool
    CHECK_PIXELVAL = 1
    QUIT = 2


class GUIFunction(Enum):
    LOG = 0  # args: str
    STARTED = 1  # args: bool
    ASK_DIRECTORY = 2  # callback: callable
    SHOW_ERROR = 3
    SET_NOTIFY = 4


def _clear_function_queue(gui: 'GUI'):
    while len(gui._function_queue) > 0:
        func = gui._function_queue.pop(0)

        if func[0] == GUIFunction.LOG:
            _write_to_console(gui, func[1][0])
        elif func[0] == GUIFunction.STARTED:
            gui._bot_running = func[1][0]
            gui._start_button["text"] = "STOP" if gui._bot_running else "START"
        elif func[0] == GUIFunction.ASK_DIRECTORY:
            messagebox.showinfo("Directory?", func[1][1])
            path = filedialog.askdirectory()
            if path != '':
                threading.Thread(target=func[1][0], args=(path,)).start()
        elif func[0] == GUIFunction.SHOW_ERROR:
            messagebox.showerror("ERROR", func[1][0])
        elif func[0] == GUIFunction.SET_NOTIFY:
            gui._notify.set(func[1][0])
            if func[1][1]:
                gui._notify_check['state'] = NORMAL
