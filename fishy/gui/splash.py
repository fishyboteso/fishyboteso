import time
from multiprocessing import Process
from tkinter import Tk, Canvas, NW
from PIL import Image, ImageTk

from fishy.helper import helper


def show():
    top = Tk()

    # top.overrideredirect(True)
    # top.lift()

    top.title("Loading...")
    top.resizable(False, False)
    top.iconbitmap(helper.manifest_file('icon.ico'))

    canvas = Canvas(top, width=300, height=200)
    canvas.pack()
    top.image = Image.open(helper.manifest_file('fishybot_logo.png')).resize((300, 200))
    top.image = ImageTk.PhotoImage(top.image)
    canvas.create_image(0, 0, anchor=NW, image=top.image)

    top.update()
    time.sleep(3)
    top.destroy()


def start():
    Process(target=show).start()
