import logging
import time
import tkinter as tk
from multiprocessing import Process, Queue
from threading import Thread

from PIL import Image, ImageTk

from fishy.helper import helper
from fishy.helper.config import config


def show(win_loc, q):
    logging.debug("started splash process")
    dim = (300, 200)
    top = tk.Tk()

    top.overrideredirect(True)
    top.lift()
    top.attributes('-topmost', True)

    top.title("Loading...")
    top.resizable(False, False)
    top.iconbitmap(helper.manifest_file('icon.ico'))

    canvas = tk.Canvas(top, width=dim[0], height=dim[1], bg='white')
    canvas.pack()
    top.image = Image.open(helper.manifest_file('fishybot_logo.png')).resize(dim)
    top.image = ImageTk.PhotoImage(top.image)
    canvas.create_image(0, 0, anchor=tk.NW, image=top.image)

    # Position splash at the center of the main window

    default_loc = (str(top.winfo_reqwidth()) + "+" + str(top.winfo_reqheight()) + "+" + "0" + "0")
    loc = (win_loc or default_loc).split(":")[-1].split("+")[1:]
    top.geometry("{}x{}+{}+{}".format(dim[0], dim[1], int(loc[0]) + int(dim[0] / 2), int(loc[1]) + int(dim[1] / 2)))

    def waiting():
        q.get()
        time.sleep(0.2)
        running[0] = False
    Thread(target=waiting).start()

    running = [True]
    while running[0]:
        top.update()
        time.sleep(0.1)

    top.destroy()
    logging.debug("ended splash process")


def create_finish(q):
    def finish():
        q.put("stop")

    return finish


def start():
    q = Queue()
    Process(target=show, args=(config.get("win_loc"), q,)).start()
    return create_finish(q)
