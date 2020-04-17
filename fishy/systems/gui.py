import time
from enum import Enum
from tkinter import *
from tkinter.ttk import *
from ttkthemes import ThemedTk
from waiting import wait
import threading

from fishy.systems.config import Config


class Callback(Enum):
    START = 0,
    SHORTCUT = 1,
    CHECK_PIXELVAL = 2,
    LOG_DUMP = 3


class GUICallback:
    def __init__(self, start_callback=None,
                 shortcut_callback=None,
                 check_pixelval_callback=None,
                 log_dump_callback=None
                 ):
        self.start_callback = start_callback
        self.shortcut_callback = shortcut_callback
        self.check_pixelval_callback = check_pixelval_callback
        self.log_dump_callback = log_dump_callback

    def call(self, callback_enum, args=None):
        to_call = None
        if callback_enum == Callback.START:
            to_call = self.start_callback
        elif callback_enum == Callback.SHORTCUT:
            to_call = self.shortcut_callback
        elif callback_enum == Callback.CHECK_PIXELVAL:
            to_call = self.check_pixelval_callback
        elif callback_enum == Callback.LOG_DUMP:
            to_call = self.log_dump_callback

        if to_call is None:
            return

        threading.Thread(target=to_call, args=(*args,)).start()


class GUI:

    def __init__(self, gui_callback=None,
                 config: Config = None):
        self.callbacks = GUICallback() if gui_callback is None else gui_callback
        self.config = config
        self.start_restart = False
        self.destroyed = True
        self.root = None
        self._log_strings = []
        self.console = None

    def create(self):
        self.root = ThemedTk(theme="equilux", background=True)
        self.root.title("Fiishybot for Elder Scrolls Online")
        self.root.geometry('650x550')

        # region menu
        menubar = Menu(self.root)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Create Shortcut", command=lambda: self.callbacks.call(Callback.SHORTCUT))
        filemenu.add_command(label="{} Dark Mode".format("Disable" if self.config.get("dark_mode", True) else "Enable"),
                             command=self._toggle_mode)
        menubar.add_cascade(label="File", menu=filemenu)

        debug_menu = Menu(menubar, tearoff=0)
        debug_menu.add_command(label="Check PixelVal",
                               command=lambda: self.callbacks.call(Callback.CHECK_PIXELVAL))
        debug_menu.add_command(label="Log Dump")
        menubar.add_cascade(label="Debug", menu=debug_menu, command=lambda: self.callbacks.call(Callback.LOG_DUMP))
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

        Button(self.root, text="START", width=25,
               command=lambda: self.callbacks.call(Callback.START,
                                                   (ip.get(), action_key_entry.get(), borderless.instate(['selected'])))
               ).pack(pady=(15, 15))
        # endregion

        self._apply_theme(self.config.get("dark_mode", True))
        self.root.update()
        self.root.minsize(self.root.winfo_width(), self.root.winfo_height())
        self.root.protocol("WM_DELETE_WINDOW", self._set_destroyed)
        self.destroyed = False
        while True:
            self.root.update()
            self._update_console()

            if self.start_restart:
                self.root.destroy()
                self.root.quit()
                self.start_restart = False
                self.create()
            if self.destroyed:
                break
            time.sleep(0.01)

    def _apply_theme(self, dark):
        self.root["theme"] = "equilux" if dark else "breeze"
        self.console["background"] = "#707070" if dark else "#ffffff"
        self.console["fg"] = "#ffffff" if dark else "#000000"

    def start(self):
        threading.Thread(target=self.create, args=()).start()

    def _toggle_mode(self):
        self.config.set("dark_mode", not self.config.get("dark_mode", True))
        self.start_restart = True

    def _set_destroyed(self):
        self.destroyed = True

    def writeToLog(self, msg):
        self._log_strings.append(msg)

    def _update_console(self):
        while len(self._log_strings) > 0:
            msg = self._log_strings.pop(0)
            numlines = self.console.index('end - 1 line').split('.')[0]
            self.console['state'] = 'normal'
            if int(numlines) >= 50:  # delete old lines
                self.console.delete(1.0, 2.0)
            if self.console.index('end-1c') != '1.0':  # new line for each log
                self.console.insert('end', '\n')
            self.console.insert('end', msg)
            self.console.see("end")  # scroll to bottom
            self.console['state'] = 'disabled'


def start(ip, actionkey, fullscreen):
    print(f"{ip}, {actionkey}, {fullscreen}")


def main():
    config = Config()
    gui = GUI(config=config, gui_callback=GUICallback(start_callback=start))
    gui.start()
    wait(lambda: not gui.destroyed)
    while not gui.destroyed:
        gui.writeToLog("yo")
        time.sleep(1)


if __name__ == '__main__':
    main()
