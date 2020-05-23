import time
from tkinter import Toplevel


def center(win):
    win.update_idletasks()
    win.master.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()

    offset_x = win.master.winfo_x() + win.master.winfo_width() // 2 - (width // 2)
    offset_y = win.master.winfo_y()+ win.master.winfo_height() // 2 - (height // 2)

    win.geometry('{}x{}+{}+{}'.format(width, height, offset_x, offset_y))


class PopUp(Toplevel):
    def __init__(self, quit_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True
        self.quit_callback  = quit_callback

    def quit_top(self):
        self.quit_callback()
        self.destroy()
        self.running = False

    def start(self):
        self.protocol("WM_DELETE_WINDOW", self.quit_top)
        self.grab_set()
        center(self)
        while self.running:
            self.update()
            time.sleep(0.01)
        self.grab_release()
