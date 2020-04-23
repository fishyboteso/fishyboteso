import logging
import os
import time
from enum import Enum
from logging import StreamHandler
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import *
from typing import Tuple, List, Callable, Optional

from ttkthemes import ThemedTk
import threading

from fishy.systems import helper
from fishy.systems.config import Config


class GUIStreamHandler(StreamHandler):
    def __init__(self, gui):
        StreamHandler.__init__(self)
        self.gui = gui

    def emit(self, record):
        msg = self.format(record)
        self.gui.call(GUIFunction.LOG, (msg,))


class GUIEvent(Enum):
    START_BUTTON = 0  # args: ip: str, action_key: str, fullscreen: bool, collect_r: bool
    CHECK_PIXELVAL = 1
    QUIT = 2


class GUIFunction(Enum):
    LOG = 0  # args: str
    STARTED = 1  # args: bool
    ASK_DIRECTORY = 2  # callback: callable


class GUI:

    def __init__(self, config: Config, event_trigger: Callable[[GUIEvent, Optional[Tuple]], None]):
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

        self.thread = threading.Thread(target=self.create, args=())

        rootLogger = logging.getLogger('')
        rootLogger.setLevel(logging.DEBUG)
        new_console = GUIStreamHandler(self)
        rootLogger.addHandler(new_console)

    def create(self):
        self.root = ThemedTk(theme="equilux", background=True)
        self.root.title("Fiishybot for Elder Scrolls Online")
        self.root.geometry('650x550')

        self.root.iconbitmap(helper.get_data_file_path('icon.ico'))

        # region menu
        menubar = Menu(self.root)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Create Shortcut", command=lambda: helper.create_shortcut(self))

        dark_mode_var = IntVar()
        dark_mode_var.set(int(self.config.get('dark_mode', True)))
        filemenu.add_checkbutton(label="Dark Mode", command=self._toggle_mode,
                                 variable=dark_mode_var)

        menubar.add_cascade(label="File", menu=filemenu)

        debug_menu = Menu(menubar, tearoff=0)
        debug_menu.add_command(label="Check PixelVal",
                               command=lambda: self._event_trigger(GUIEvent.CHECK_PIXELVAL))

        debug_var = IntVar()
        debug_var.set(int(self.config.get('debug', False)))

        def keep_console():
            self.config.set("debug", bool(debug_var.get()))
            logging.debug("Restart to update the changes")
        debug_menu.add_checkbutton(label="Keep Console", command=keep_console, variable=debug_var)

        debug_menu.add_command(label="Log Dump", command=lambda: logging.error("Not Implemented"))
        menubar.add_cascade(label="Debug", menu=debug_menu)

        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Troubleshoot Guide", command=lambda: logging.debug("Not Implemented"))
        help_menu.add_command(label="Need Help?", command=lambda: helper.open_web("http://discord.definex.in"))
        help_menu.add_command(label="Donate", command=lambda: helper.open_web("https://paypal.me/AdamSaudagar"))
        menubar.add_cascade(label="Help", menu=help_menu)

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

        Label(left_frame, text="Android IP").grid(row=0, column=0)
        ip = Entry(left_frame)
        ip.insert(0, self.config.get("ip", ""))
        ip.grid(row=0, column=1)

        Label(left_frame, text="Fullscreen: ").grid(row=1, column=0, pady=(5, 5))
        borderless = Checkbutton(left_frame, variable=IntVar(value=int(self.config.get("borderless", False))))
        borderless.grid(row=1, column=1)

        left_frame.grid(row=0, column=0)

        right_frame = Frame(controls_frame)

        Label(right_frame, text="Action Key:").grid(row=0, column=0)
        action_key_entry = Entry(right_frame)
        action_key_entry.grid(row=0, column=1)
        action_key_entry.insert(0, self.config.get("action_key", "e"))

        Label(right_frame, text="Collect R: ").grid(row=1, column=0, pady=(5, 5))
        collect_r = Checkbutton(right_frame, variable=IntVar(value=1 if self.config.get("collect_r", False) else 0))
        collect_r.grid(row=1, column=1)

        right_frame.grid(row=0, column=1, padx=(50, 0))

        controls_frame.pack()

        self.start_button = Button(self.root, text="STOP" if self._bot_running else "START", width=25)

        def start_button_callback():
            args = (ip.get(),
                    action_key_entry.get(),
                    borderless.instate(['selected']),
                    collect_r.instate(['selected']))
            self._event_trigger(GUIEvent.START_BUTTON, args)
            self._save_config(*args)

        self.start_button["command"] = start_button_callback
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
                self._event_trigger(GUIEvent.QUIT)
                break
            time.sleep(0.01)

    def _clear_function_queue(self):
        while len(self._function_queue) > 0:
            func = self._function_queue.pop(0)

            if func[0] == GUIFunction.LOG:
                self._write_to_console(func[1][0])
            elif func[0] == GUIFunction.STARTED:
                self._bot_running = func[1][0]
                self.start_button["text"] = "STOP" if self._bot_running else "START"
            elif func[0] == GUIFunction.ASK_DIRECTORY:
                messagebox.showinfo("Directory?", func[1][1])
                path = filedialog.askdirectory()
                if path != '':
                    threading.Thread(target=func[1][0], args=(path,)).start()

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

    def _save_config(self, ip, action_key, borderless, collect_r):
        self.config.set("ip", ip, False)
        self.config.set("action_key", action_key, False)
        self.config.set("borderless", borderless, False)
        self.config.set("collect_r", collect_r, False)
        self.config.save_config()

    def start(self):
        self.thread.start()

    def call(self, gui_func: GUIFunction, args: Tuple = None):
        self._function_queue.append((gui_func, args))
