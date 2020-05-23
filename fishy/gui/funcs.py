from tkinter import messagebox, NORMAL


# noinspection PyProtectedMember
class GUIFuncs:
    def __init__(self, gui):
        self.gui = gui

    def show_error(self, error):
        self.gui.call_in_thread(lambda: messagebox.showerror("ERROR", error))

    def bot_started(self, started):
        def func():
            self.gui._bot_running = started
            self.gui._start_button["text"] = "STOP" if self.gui._bot_running else "START"

        self.gui.call_in_thread(func)
