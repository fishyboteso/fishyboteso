import os
import tempfile
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
import pyqrcode

from fishy import web
import typing

if typing.TYPE_CHECKING:
    from . import GUI


def _give_notification_link(gui: 'GUI'):
    if web.is_subbed(gui._config.get("uid"))[0]:
        web.unsub(gui._config.get("uid"))
        return

    # set notification checkbutton
    gui._notify.set(0)

    def quit_top():
        top.destroy()
        top_running[0] = False

    def check():
        if web.is_subbed(gui._config.get("uid"), False)[0]:
            gui._notify.set(1)
            web.send_notification(gui._config.get("uid"), "Sending a test notification :D")
            messagebox.showinfo("Note!", "Notification configured successfully!")
            quit_top()
        else:
            messagebox.showerror("Error", "Subscription wasn't successful")

    print("got to {}".format(web.get_notification_page(gui._config.get("uid"))))
    qrcode = pyqrcode.create(web.get_notification_page(gui._config.get("uid")))
    t = os.path.join(tempfile.gettempdir(), "fishyqr.png")
    qrcode.png(t, scale=8)

    top_running = [True]

    top = Toplevel(background=gui._root["background"])
    top.minsize(width=500, height=500)
    top.title("Notification Setup")

    Label(top, text="Step 1.").pack(pady=(5, 5))
    Label(top, text="Scan the QR Code on your Phone and press \"Enable Notification\"").pack(pady=(5, 5))
    canvas = Canvas(top, width=qrcode.get_png_size(8), height=qrcode.get_png_size(8))
    canvas.pack(pady=(5, 5))
    Label(top, text="Step 2.").pack(pady=(5, 5))
    Button(top, text="Check", command=check).pack(pady=(5, 5))

    image = PhotoImage(file=t)
    canvas.create_image(0, 0, anchor=NW, image=image)

    top.protocol("WM_DELETE_WINDOW", quit_top)
    top.grab_set()
    while top_running[0]:
        top.update()
    top.grab_release()
