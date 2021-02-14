import time
from multiprocessing import Process
from tkinter import *
from PIL import Image, ImageTk

from fishy.helper.config import config
from fishy.helper import helper


def show():
    dim=(300,200)
    top = Tk()

    top.overrideredirect(True)
    top.lift()

    top.title("Loading...")
    top.resizable(False, False)
    top.iconbitmap(helper.manifest_file('icon.ico'))

    canvas = Canvas(top, width=dim[0], height=dim[1], bg='white')
    canvas.pack()
    top.image = Image.open(helper.manifest_file('fishybot_logo.png')).resize(dim)
    top.image = ImageTk.PhotoImage(top.image)
    canvas.create_image(0, 0, anchor=NW, image=top.image)

    # Position splash at the center of the main window
    win_loc = config.get("win_loc", str(top.winfo_reqwidth())+"+"+str(top.winfo_reqheight())+"+"+"0"+"0").split("+")[1:]
    top.geometry("{}x{}+{}+{}".format(dim[0], dim[1], int(win_loc[0])+int(dim[0]/2), int(win_loc[1])+int(dim[1]/2)))

    top.update()
    time.sleep(3)
    top.destroy()


def start():
    Process(target=show).start()
