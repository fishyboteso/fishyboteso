from tkinter import messagebox

import typing
if typing.TYPE_CHECKING:
    from fishy.gui import GUI


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

        self.gui.call_in_thread(func)

    def quit(self):
        def func():
            self.gui._root.destroy()

        self.gui.call_in_thread(func)
