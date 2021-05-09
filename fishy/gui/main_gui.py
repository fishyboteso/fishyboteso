import logging
import time
import tkinter as tk
import tkinter.ttk as ttk
import typing

from ttkthemes import ThemedTk

from fishy import helper
from fishy.helper import hotkey
from fishy.web import web

from ..constants import chalutier, lam2
from ..helper.config import config
from ..helper.hotkey import Key
from .discord_login import discord_login

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
    if config.get("dont_ask_update", False):
        filemenu.add_command(label="Update", command=helper.update)

    def installer():
        if filemenu.entrycget(4, 'label') == "Remove Chalutier":
            if helper.remove_addon(chalutier[0]) == 0:
                filemenu.entryconfigure(4, label="Install Chalutier")
        else:
            r = helper.install_addon(*chalutier)
            r += helper.install_addon(*lam2)
            if r == 0:
                filemenu.entryconfigure(4, label="Remove Chalutier")
    chaEntry = "Remove Chalutier" if helper.addon_exists(chalutier[0]) else "Install Chalutier"
    filemenu.add_command(label=chaEntry, command=installer)
    menubar.add_cascade(label="Options", menu=filemenu)

    debug_menu = tk.Menu(menubar, tearoff=0)
    debug_menu.add_command(label="Check PixelVal",
                           command=lambda: gui.engine.check_pixel_val())

    debug_var = tk.IntVar()
    debug_var.set(int(config.get('debug', False)))

    def keep_console():
        config.set("debug", bool(debug_var.get()))
        logging.debug("Restart to update the changes")

    debug_menu.add_checkbutton(label="Keep Console", command=keep_console, variable=debug_var)
    debug_menu.add_command(label="Restart", command=helper.restart)
    menubar.add_cascade(label="Debug", menu=debug_menu)

    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="Need Help?", command=lambda: helper.open_web("http://discord.definex.in"))
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

    gui._config_button = ttk.Button(start_frame, text="⚙", width=0, command=lambda: engines[gui._engine_var.get()][0]())
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
        gui._root.geometry(config.get("win_loc"))

    hotkey.set_hotkey(Key.F9, gui.funcs.start_engine)

    # noinspection PyProtectedMember
    def set_destroy():
        if gui._bot_running:
            if not tk.messagebox.askyesno(title="Quit?", message="Bot engine running. Quit Anyway?"):
                return

        config.set("win_loc", gui._root.geometry())
        gui._destroyed = True

    gui._root.protocol("WM_DELETE_WINDOW", set_destroy)
    gui._destroyed = False

    while True:
        gui._root.update()
        gui._clear_function_queue()
        if gui._start_restart:
            gui._root.destroy()
            gui._root.quit()
            gui._start_restart = False
            gui.create()
        if gui._destroyed:
            gui.engine.quit()
            break
        time.sleep(0.01)
