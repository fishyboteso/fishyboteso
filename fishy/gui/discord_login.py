import time
from tkinter import Toplevel, CENTER, BOTH, messagebox
from tkinter.ttk import Entry, Button

import typing

from fishy.helper import helper

from fishy.web import web

from fishy.libs.tkhtmlview import HTMLLabel
from ..helper.config import config

if typing.TYPE_CHECKING:
    from . import GUI


# noinspection PyProtectedMember
def discord_login(gui: 'GUI'):
    if web.is_logged_in(config.get("uid")):
        if web.logout(config.get("uid")):
            gui.login.set(0)
        return

    # set notification checkbutton
    gui.login.set(0)

    def quit_top():
        top.destroy()
        top_running[0] = False

    def check():
        code = int(login_code.get()) if login_code.get().isdigit() else 0
        if web.login(config.get("uid"), code):
            gui.login.set(1)
            messagebox.showinfo("Note!", "Logged in successfuly!")
            quit_top()
        else:
            messagebox.showerror("Error", "Logged wasn't successful")

    top_running = [True]

    top = Toplevel(background=gui._root["background"])
    top.minsize(width=300, height=300)
    top.title("Notification Setup")

    html_label = HTMLLabel(top,
                           html=f'<div style="color: {gui._console["fg"]}; text-align: center">'
                                f'<p><span style="font-size:20px">Step 1.</span><br/>'
                                f'Join <a href="https://discord.definex.in/">Discord server</a></p>'
                                f'<p><span style="font-size:20px">Step 2.</span><br/>'
                                f'run !login command in #bot-spam channel'
                                f'<p><span style="font-size:20px">Step 3.</span><br/>'
                                f'enter login code'
                                f'</div>', background=gui._root["background"])

    html_label.pack(pady=(20, 5))
    html_label.fit_height()

    login_code = Entry(top, justify=CENTER, font="Calibri 15")
    login_code.pack(padx=(15, 15), expand=True, fill=BOTH)

    html_label = HTMLLabel(top,
                           html=f'<div style="color: {gui._console["fg"]}; text-align: center">'
                                f'<p><span style="font-size:20px">Step 4.</span><br/></p>'
                                f'</div>', background=gui._root["background"])

    html_label.pack(pady=(5, 5))
    html_label.fit_height()

    Button(top, text="REGISTER", command=check).pack(pady=(5, 20))

    top.protocol("WM_DELETE_WINDOW", quit_top)
    top.grab_set()
    while top_running[0]:
        top.update()
        time.sleep(0.01)
    top.grab_release()
