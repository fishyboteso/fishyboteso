import time
import tkinter as tk
import tkinter.ttk as ttk
import typing

from fishy.libs.tkhtmlview import HTMLLabel
from fishy.web import web

from ..helper.config import config

if typing.TYPE_CHECKING:
    from . import GUI


# noinspection PyProtectedMember
def discord_login(gui: 'GUI'):
    if web.is_logged_in():
        if web.logout():
            gui.login.set(0)
        return

    # set notification checkbutton
    gui.login.set(0)

    def quit_top():
        top.destroy()
        top_running[0] = False

    # noinspection PyUnresolvedReferences
    def check():
        code = int(login_code.get()) if login_code.get().isdigit() else 0
        if web.login(config.get("uid"), code):
            gui.login.set(1)
            tk.messagebox.showinfo("Note!", "Login successful!")
            quit_top()
        else:
            tk.messagebox.showerror("Error", "Login was not successful!")

    top_running = [True]

    top = tk.Toplevel(background=gui._root["background"])
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

    login_code = ttk.Entry(top, justify=tk.CENTER, font="Calibri 15")
    login_code.pack(padx=(15, 15), expand=True, fill=tk.BOTH)

    html_label = HTMLLabel(top,
                           html=f'<div style="color: {gui._console["fg"]}; text-align: center">'
                                f'<p><span style="font-size:20px">Step 4.</span><br/></p>'
                                f'</div>', background=gui._root["background"])

    html_label.pack(pady=(5, 5))
    html_label.fit_height()

    ttk.Button(top, text="REGISTER", command=check).pack(pady=(5, 20))

    top.protocol("WM_DELETE_WINDOW", quit_top)
    top.grab_set()
    while top_running[0]:
        top.update()
        time.sleep(0.01)
    top.grab_release()
