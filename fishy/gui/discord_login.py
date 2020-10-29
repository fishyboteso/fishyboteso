import time
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

from fishy import web
import typing

from fishy.libs.tkhtmlview import HTMLLabel
from ..helper.config import config

if typing.TYPE_CHECKING:
    from . import GUI


# noinspection PyProtectedMember
def discord_login(gui: 'GUI'):
    if web.is_subbed(config.get("uid"))[0]:
        web.unsub(config.get("uid"))
        return

    # set notification checkbutton
    gui._notify.set(0)

    def quit_top():
        top.destroy()
        top_running[0] = False

    def check():
        if web.sub(config.get("uid"), discord_name.get()):
            if web.is_subbed(config.get("uid"), False)[0]:
                gui._notify.set(1)
                messagebox.showinfo("Note!", "Notification configured successfully!")
                quit_top()
        else:
            messagebox.showerror("Error", "Subscription wasn't successful")

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

    discord_name = Entry(top, justify=CENTER, font="Calibri 15")
    discord_name.pack(padx=(15, 15), expand=True, fill=BOTH)

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
