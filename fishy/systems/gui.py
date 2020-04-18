import logging
import time
from enum import Enum
from logging import StreamHandler
from tkinter import *
from tkinter.ttk import *
from typing import Tuple, List, Callable

from ttkthemes import ThemedTk
from waiting import wait
import threading

from fishy.systems.config import Config


class GUIStreamHandler(StreamHandler):
    def __init__(self, gui):
        StreamHandler.__init__(self)
        self.gui = gui

    def emit(self, record):
        msg = self.format(record)
        self.gui.call(GUIFunction.LOG, (msg,))


class GUIEvent(Enum):
    START_BUTTON = 0  # args: ip: str, action_key: str, fullscreen: bool
    CHECK_PIXELVAL = 1


class GUIFunction(Enum):
    LOG = 0  # args: str
    STARTED = 1  # args: bool


class GUI:

    def __init__(self, config: Config, event_trigger: Callable[[GUIEvent, Tuple], None]):
        self.config = config
        self.start_restart = False
        self.destroyed = True
        self._log_strings = []
        self._function_queue: List[Tuple[GUIFunction, Tuple]] = []
        self._event_trigger = event_trigger
        self._bot_running = False

        # UI items
        self.root = None
        self.console = None
        self.start_button = None

    def create(self):
        self.root = ThemedTk(theme="equilux", background=True)
        self.root.title("Fiishybot for Elder Scrolls Online")
        self.root.geometry('650x550')

        # region menu
        menubar = Menu(self.root)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Create Shortcut", command=lambda: logging.error("Not Implemented"))
        filemenu.add_command(label="{} Dark Mode".format("Disable" if self.config.get("dark_mode", True) else "Enable"),
                             command=self._toggle_mode)
        menubar.add_cascade(label="File", menu=filemenu)

        debug_menu = Menu(menubar, tearoff=0)
        debug_menu.add_command(label="Check PixelVal",
                               command=lambda: logging.error("Not Implemented"))
        debug_menu.add_command(label="Log Dump")
        menubar.add_cascade(label="Debug", menu=debug_menu, command=lambda: logging.error("Not Implemented"))
        self.root.config(menu=menubar)
        # endregion

        # region console
        self.console = Text(self.root, state='disabled', wrap='none', background="#707070", fg="#ffffff")
        self.console.pack(fill=BOTH, expand=True, pady=(15, 15), padx=(5, 5))
        self.console.mark_set("sentinel", INSERT)
        self.console.config(state=DISABLED)

        controls_frame = Frame(self.root)
        # endregion

        # region controls
        left_frame = Frame(controls_frame)

        Label(left_frame, text="IP").grid(row=0, column=0)
        ip = Entry(left_frame)
        ip.grid(row=0, column=1)

        Label(left_frame, text="Fullscreen: ").grid(row=1, column=0, pady=(5, 5))
        borderless = Checkbutton(left_frame)
        borderless.grid(row=1, column=1)

        left_frame.grid(row=0, column=0)

        right_frame = Frame(controls_frame)

        Label(right_frame, text="Action Key:").grid(row=0, column=0)
        action_key_entry = Entry(right_frame)
        action_key_entry.grid(row=0, column=1)
        action_key_entry.insert(0, "e")

        Label(right_frame, text="Press start").grid(row=1, columnspan=2, pady=(5, 5))

        right_frame.grid(row=0, column=1, padx=(50, 0))

        controls_frame.pack()

        self.start_button = Button(self.root, text="START", width=25)
        self.start_button["command"] = lambda: self._event_trigger(GUIEvent.START_BUTTON, (ip.get(),
                                                                                           action_key_entry.get(),
                                                                                           borderless.instate(
                                                                                               ['selected'])))
        self.start_button.pack(pady=(15, 15))
        # endregion

        self._apply_theme(self.config.get("dark_mode", True))
        self.root.update()
        self.root.minsize(self.root.winfo_width(), self.root.winfo_height())
        self.root.protocol("WM_DELETE_WINDOW", self._set_destroyed)
        self.destroyed = False

        while True:
            self.root.update()
            self._clear_function_queue()
            if self.start_restart:
                self.root.destroy()
                self.root.quit()
                self.start_restart = False
                self.create()
            if self.destroyed:
                break
            time.sleep(0.01)

    def _clear_function_queue(self):
        while len(self._function_queue) > 0:
            func = self._function_queue.pop(0)

            if func[0] == GUIFunction.LOG:
                self._write_to_console(func[1][0])
            elif func[1] == GUIFunction.STARTED:
                self.start_button["text"] = "STOP" if func[1][0] else "START"

    def _apply_theme(self, dark):
        self.root["theme"] = "equilux" if dark else "breeze"
        self.console["background"] = "#707070" if dark else "#ffffff"
        self.console["fg"] = "#ffffff" if dark else "#000000"

    def _toggle_mode(self):
        self.config.set("dark_mode", not self.config.get("dark_mode", True))
        self.start_restart = True

    def _set_destroyed(self):
        self.destroyed = True

    def _write_to_console(self, msg):
        numlines = self.console.index('end - 1 line').split('.')[0]
        self.console['state'] = 'normal'
        if int(numlines) >= 50:  # delete old lines
            self.console.delete(1.0, 2.0)
        if self.console.index('end-1c') != '1.0':  # new line for each log
            self.console.insert('end', '\n')
        self.console.insert('end', msg)
        self.console.see("end")  # scroll to bottom
        self.console['state'] = 'disabled'

    def start(self):
        threading.Thread(target=self.create, args=()).start()

    def call(self, gui_func: GUIFunction, args):
        self._function_queue.append((gui_func, args))

# def start(ip, actionkey, fullscreen):
#     logging.info(f"{ip}, {actionkey}, {fullscreen}")
#
#
# def main():
#     config = Config()
#     gui = GUI(config=config, gui_callback=GUICallback(start_callback=start))
#     gui.start()
#     wait(lambda: not gui.destroyed)
#     while not gui.destroyed:
#         gui.writeToLog("yo")
#         time.sleep(1)
#
#
# if __name__ == '__main__':
#     main()
