import typing
from tkinter import messagebox

from fishy.helper.config import config

if typing.TYPE_CHECKING:
    from fishy.gui import GUI


class GUIFuncsMock:
    def __init__(self):
        ...

    def show_error(self, error):
        ...

    def bot_started(self, started):
        ...

    def quit(self):
        ...

    def start_engine(self):
        ...


# noinspection PyProtectedMember
class GUIFuncs:
    def __init__(self, gui: 'GUI'):
        self.gui = gui

    def show_error(self, error):
        self.gui.call_in_thread(lambda: messagebox.showerror("ERROR", error))

    def bot_started(self, started):
        def func():
            self.gui._bot_running = started
            self.gui._start_button["text"] = self.gui._get_start_stop_text()
            self.gui._engine_select["state"] = "disabled" if self.gui._bot_running else "normal"
            self.gui._config_button["state"] = "disabled" if self.gui._bot_running else "normal"

        self.gui.call_in_thread(func)

    def quit(self):
        def func():
            self.gui._root.destroy()

        self.gui.call_in_thread(func)

    def start_engine(self):
        def start_engine():
            config.set("last_started", self.gui._engine_var.get())
            self.gui.engines[self.gui._engine_var.get()].start()
        self.gui.call_in_thread(start_engine)
