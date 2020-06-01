import logging
import time
from tkinter import *
from tkinter.ttk import *
from ttkthemes import ThemedTk

from fishy import helper, web
from fishy.gui import config_top

import typing

from fishy.helper import not_implemented

if typing.TYPE_CHECKING:
    from . import GUI


def _apply_theme(gui: 'GUI'):
    dark = gui._config.get("dark_mode", True)
    gui._root["theme"] = "equilux" if dark else "breeze"
    gui._console["background"] = "#707070" if dark else "#ffffff"
    gui._console["fg"] = "#ffffff" if dark else "#000000"


def _create(gui: 'GUI'):
    engines = {
        "Semi Fisher": [lambda: config_top.start_semifisher_config(gui), gui.engine.toggle_semifisher],
        "Full-Auto Fisher": [not_implemented, gui.engine.toggle_fullfisher],
        # "Lock Picker": [not_implemented, not_implemented]
    }

    def start_engine(label):
        gui._config.set("last_started", label)
        engines[label][1]()

    gui._root = ThemedTk(theme="equilux", background=True)
    gui._root.title("Fishybot for Elder Scrolls Online")

    gui._root.iconbitmap(helper.manifest_file('icon.ico'))

    # region menu
    menubar = Menu(gui._root)

    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Create Shortcut", command=helper.create_shortcut)

    def _toggle_mode():
        gui._config.set("dark_mode", not gui._config.get("dark_mode", True))
        gui._start_restart = True

    dark_mode_var = IntVar()
    dark_mode_var.set(int(gui._config.get('dark_mode', True)))
    filemenu.add_checkbutton(label="Dark Mode", command=_toggle_mode,
                             variable=dark_mode_var)

    menubar.add_cascade(label="File", menu=filemenu)

    debug_menu = Menu(menubar, tearoff=0)
    debug_menu.add_command(label="Check PixelVal",
                           command=lambda: gui.engine.check_pixel_val())

    debug_var = IntVar()
    debug_var.set(int(gui._config.get('debug', False)))

    def keep_console():
        gui._config.set("debug", bool(debug_var.get()))
        logging.debug("Restart to update the changes")

    debug_menu.add_checkbutton(label="Keep Console", command=keep_console, variable=debug_var)
    debug_menu.add_command(label="Log Dump", command=not_implemented)
    debug_menu.add_command(label="Restart", command=helper.restart)
    menubar.add_cascade(label="Debug", menu=debug_menu)

    help_menu = Menu(menubar, tearoff=0)
    help_menu.add_command(label="Troubleshoot Guide", command=not_implemented)
    help_menu.add_command(label="Need Help?", command=lambda: helper.open_web("http://discord.definex.in"))
    help_menu.add_command(label="Donate", command=lambda: helper.open_web("https://paypal.me/AdamSaudagar"))
    menubar.add_cascade(label="Help", menu=help_menu)

    gui._root.config(menu=menubar)
    # endregion

    # region console
    gui._console = Text(gui._root, state='disabled', wrap='none', background="#707070", fg="#ffffff")
    gui._console.pack(fill=BOTH, expand=True, pady=(15, 15), padx=(10, 10))
    gui._console.mark_set("sentinel", INSERT)
    gui._console.config(state=DISABLED)
    # endregion

    # region controls
    start_frame = Frame(gui._root)

    engine_var = StringVar(start_frame)
    labels = list(engines.keys())
    last_started = gui._config.get("last_started", labels[0])
    engine_select = OptionMenu(start_frame, engine_var, last_started, *labels)
    engine_select.pack(side=LEFT)

    config_button = Button(start_frame, text="⚙", width=0, command=lambda: engines[engine_var.get()][0]())
    config_button.pack(side=RIGHT)

    gui._start_button = Button(start_frame, text="STOP" if gui._bot_running else "START", width=25,
                               command=lambda: start_engine(engine_var.get()))
    gui._start_button.pack(side=RIGHT)

    start_frame.pack(padx=(10, 10), pady=(5, 15), fill=X)
    # endregion

    _apply_theme(gui)
    gui._root.update()
    gui._root.minsize(gui._root.winfo_width() + 10, gui._root.winfo_height() + 10)

    def set_destroy():
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
