import logging
import threading
import time
from tkinter import *
from tkinter.ttk import *
from ttkthemes import ThemedTk

from fishy import helper, web

from .comms import GUIEvent, GUIFunction, _clear_function_queue
from .notification import _give_notification_link
import typing

if typing.TYPE_CHECKING:
    from . import GUI


def _apply_theme(gui: 'GUI'):
    dark = gui._config.get("dark", True)
    gui._root["theme"] = "equilux" if dark else "breeze"
    gui._console["background"] = "#707070" if dark else "#ffffff"
    gui._console["fg"] = "#ffffff" if dark else "#000000"


def _create(gui: 'GUI'):
    gui._root = ThemedTk(theme="equilux", background=True)
    gui._root.title("Fishybot for Elder Scrolls Online")
    gui._root.geometry('650x550')

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
                           command=lambda: gui._event_trigger(GUIEvent.CHECK_PIXELVAL, ()))

    debug_var = IntVar()
    debug_var.set(int(gui._config.get('debug', False)))

    def keep_console():
        gui._config.set("debug", bool(debug_var.get()))
        logging.debug("Restart to update the changes")

    debug_menu.add_checkbutton(label="Keep Console", command=keep_console, variable=debug_var)
    debug_menu.add_command(label="Log Dump", command=lambda: logging.error("Not Implemented"))
    debug_menu.add_command(label="Restart", command=helper.restart)
    menubar.add_cascade(label="Debug", menu=debug_menu)

    help_menu = Menu(menubar, tearoff=0)
    help_menu.add_command(label="Troubleshoot Guide", command=lambda: logging.debug("Not Implemented"))
    help_menu.add_command(label="Need Help?", command=lambda: helper.open_web("http://discord.definex.in"))
    help_menu.add_command(label="Donate", command=lambda: helper.open_web("https://paypal.me/AdamSaudagar"))
    menubar.add_cascade(label="Help", menu=help_menu)

    gui._root.config(menu=menubar)
    # endregion

    # region console
    gui._console = Text(gui._root, state='disabled', wrap='none', background="#707070", fg="#ffffff")
    gui._console.pack(fill=BOTH, expand=True, pady=(15, 15), padx=(5, 5))
    gui._console.mark_set("sentinel", INSERT)
    gui._console.config(state=DISABLED)

    controls_frame = Frame(gui._root)
    # endregion

    # region controls
    left_frame = Frame(controls_frame)

    Label(left_frame, text="Notification:").grid(row=0, column=0)

    gui._notify = IntVar(0)
    gui._notify_check = Checkbutton(left_frame, command=lambda: _give_notification_link(gui),
                                    variable=gui._notify)
    gui._notify_check.grid(row=0, column=1)
    gui._notify_check['state'] = DISABLED

    def update_notify_check():
        is_subbed = web.is_subbed(gui._config.get('uid'))
        gui.call(GUIFunction.SET_NOTIFY, (int(is_subbed[0]), is_subbed[1]))

    threading.Thread(target=update_notify_check).start()

    Label(left_frame, text="Fullscreen: ").grid(row=1, column=0, pady=(5, 5))
    borderless = Checkbutton(left_frame, )
    borderless.grid(row=1, column=1)

    left_frame.grid(row=0, column=0)

    right_frame = Frame(controls_frame)

    Label(right_frame, text="Action Key:").grid(row=0, column=0)
    action_key_entry = Entry(right_frame)
    action_key_entry.grid(row=0, column=1)
    action_key_entry.insert(0, gui._config.get("action_key", "e"))

    Label(right_frame, text="Collect R: ").grid(row=1, column=0, pady=(5, 5))
    collect_r = Checkbutton(right_frame, variable=IntVar(value=1 if gui._config.get("collect_r", False) else 0))
    collect_r.grid(row=1, column=1)

    right_frame.grid(row=0, column=1, padx=(50, 0))

    controls_frame.pack()

    gui._start_button = Button(gui._root, text="STOP" if gui._bot_running else "START", width=25)

    def start_button_callback():
        args = (action_key_entry.get(),
                borderless.instate(['selected']),
                collect_r.instate(['selected']))
        gui._event_trigger(GUIEvent.START_BUTTON, args)

        gui._config.set("action_key", action_key_entry.get(), False)
        gui._config.set("borderless", borderless.instate(['selected']), False)
        gui._config.set("collect_r", collect_r.instate(['selected']), False)
        gui._config.save_config()

    gui._start_button["command"] = start_button_callback
    gui._start_button.pack(pady=(15, 15))
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
        _clear_function_queue(gui)
        if gui._start_restart:
            gui._root.destroy()
            gui._root.quit()
            gui._start_restart = False
            gui.create()
        if gui._destroyed:
            gui._event_trigger(GUIEvent.QUIT, ())
            break
        time.sleep(0.01)
