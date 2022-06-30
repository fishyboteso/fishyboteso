import logging
import time
import tkinter as tk
import tkinter.ttk as ttk
import typing

from fishy.gui import update_dialog
from ttkthemes import ThemedTk

from fishy import helper
from fishy.web import web

from ..constants import fishyqr
from ..helper.config import config
from .discord_login import discord_login
from ..helper.hotkey.hotkey_process import hotkey
from ..helper.hotkey.process import Key

if typing.TYPE_CHECKING:
    from . import GUI


def _apply_theme(gui: 'GUI'):
    dark = config.get("dark_mode", True)
    gui._root["theme"] = "equilux" if dark else "breeze"
    gui._console["background"] = "#707070" if dark else "#ffffff"
    gui._console["fg"] = "#ffffff" if dark else "#000000"


# noinspection PyProtectedMember
def _create(gui: 'GUI'):
    engines = gui.engines

    gui._root = ThemedTk(theme="equilux", background=True)
    gui._root.attributes('-alpha', 0.0)
    gui._root.title("Fishybot for Elder Scrolls Online")
    gui._root.iconbitmap(helper.manifest_file('icon.ico'))

    # region menu
    menubar = tk.Menu(gui._root)

    filemenu = tk.Menu(menubar, tearoff=0)

    login = web.is_logged_in()
    gui.login = tk.IntVar()
    gui.login.set(1 if login > 0 else 0)
    state = tk.DISABLED if login == -1 else tk.ACTIVE
    filemenu.add_checkbutton(label="Login", command=lambda: discord_login(gui), variable=gui.login, state=state)
    filemenu.add_command(label="Create Shortcut", command=lambda: helper.create_shortcut(False))
    # filemenu.add_command(label="Create Anti-Ghost Shortcut", command=lambda: helper.create_shortcut(True))

    def _toggle_mode():
        config.set("dark_mode", not config.get("dark_mode", True))
        gui._start_restart = True

    dark_mode_var = tk.IntVar()
    dark_mode_var.set(int(config.get('dark_mode', True)))
    filemenu.add_checkbutton(label="Dark Mode", command=_toggle_mode,
                             variable=dark_mode_var)

    def update():
        config.delete("dont_ask_update")
        update_dialog.check_update(gui, True)
    filemenu.add_command(label="Update", command=update)

    def installer():
        if filemenu.entrycget(4, 'label') == "Remove FishyQR":
            if helper.remove_addon(fishyqr[0]) == 0:
                filemenu.entryconfigure(4, label="Install FishyQR")
        else:
            helper.install_required_addons(True)
            filemenu.entryconfigure(4, label="Remove FishyQR")
    chaEntry = "Remove FishyQR" if helper.addon_exists(fishyqr[0]) else "Install FishyQR"
    filemenu.add_command(label=chaEntry, command=installer)
    menubar.add_cascade(label="Options", menu=filemenu)

    debug_menu = tk.Menu(menubar, tearoff=0)
    debug_menu.add_command(label="Check QR Value",
                           command=lambda: gui.engine.check_qr_val())

    debug_var = tk.IntVar()
    debug_var.set(int(config.get('debug', False)))

    def keep_console():
        config.set("debug", bool(debug_var.get()))
        logging.debug("Restart to update the changes")

    debug_menu.add_checkbutton(label="Keep Console", command=keep_console, variable=debug_var)
    menubar.add_cascade(label="Debug", menu=debug_menu)

    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="Need Help?", command=lambda: helper.open_web("https://github.com/fishyboteso/fishyboteso/wiki"))
    help_menu.add_command(label="Donate", command=lambda: helper.open_web("https://paypal.me/AdamSaudagar"))
    menubar.add_cascade(label="Help", menu=help_menu)

    gui._root.config(menu=menubar)
    # endregion

    # region console
    gui._console = tk.Text(gui._root, state='disabled', wrap='none', background="#707070", fg="#ffffff")
    gui._console.pack(fill=tk.BOTH, expand=True, pady=(15, 15), padx=(10, 10))
    gui._console.mark_set("sentinel", tk.INSERT)
    gui._console.config(state=tk.DISABLED)
    # endregion

    # region controls
    start_frame = ttk.Frame(gui._root)

    gui._engine_var = tk.StringVar(start_frame)
    labels = list(engines.keys())
    last_started = config.get("last_started", labels[0])
    gui._engine_select = ttk.OptionMenu(start_frame, gui._engine_var, last_started, *labels)
    gui._engine_select.pack(side=tk.LEFT)

    gui._config_button = ttk.Button(start_frame, text="⚙", width=0,
                                    command=lambda: engines[gui._engine_var.get()].config())
    gui._config_button.pack(side=tk.RIGHT)

    gui._start_button = ttk.Button(start_frame, text=gui._get_start_stop_text(), width=25,
                                   command=gui.funcs.start_engine)
    gui._start_button.pack(side=tk.RIGHT)

    start_frame.pack(padx=(10, 10), pady=(5, 15), fill=tk.X)
    # endregion

    _apply_theme(gui)
    gui._root.update()

    gui._root.minsize(gui._root.winfo_width() + 10, gui._root.winfo_height() + 10)
    if config.get("win_loc") is not None:
        gui._root.geometry(config.get("win_loc").split(":")[-1])
        if config.get("win_loc").split(":")[0] == "zoomed":
            gui._root.update()
            gui._root.state("zoomed")

    hotkey.hook(Key.F9, gui.funcs.start_engine)

    # noinspection PyProtectedMember,PyUnresolvedReferences
    def set_destroy():
        if gui._bot_running:
            if not tk.messagebox.askyesno(title="Quit?", message="Bot engine running. Quit Anyway?"):
                return

        if gui._root.state() == "zoomed":
            # setting it to normal first is done to keep user-changed geometry values
            gui._root.state("normal")
            config.set("win_loc", "zoomed" + ":" + gui._root.geometry())
        else:
            config.set("win_loc", gui._root.state() + ":" + gui._root.geometry())

        gui._destroyed = True

    gui._root.protocol("WM_DELETE_WINDOW", set_destroy)
    gui._destroyed = False

    gui._root.update()
    gui._clear_function_queue()
    gui._root.after(0, gui._root.attributes, "-alpha", 1.0)
    gui.on_ready()
    while True:
        gui._root.update()
        gui._clear_function_queue()
        if gui._start_restart:
            gui._root.destroy()
            gui._root.quit()
            gui._start_restart = False
            gui.create()
        if gui._destroyed:
            gui.engine.quit_me()
            break
        time.sleep(0.01)
