import logging
import os
import typing
from tkinter.filedialog import askopenfilename

from fishy.helper import helper

from fishy import web

import tkinter as tk
import tkinter.ttk as ttk

from fishy.helper.config import config
from fishy.helper.popup import PopUp

if typing.TYPE_CHECKING:
    from fishy.gui import GUI


def start_fullfisher_config(gui: 'GUI'):
    top = PopUp(helper.empty_function, gui._root, background=gui._root["background"])
    controls_frame = ttk.Frame(top)
    top.title("Config")

    def file_name():
        file = config.get("full_auto_rec_file", None)
        if file is None:
            return "Not Selected"
        return os.path.basename(file)

    def select_file():
        file = askopenfilename(filetypes=[('Python Files', '*.fishy')])
        if not file:
            logging.error("file not selected")
        else:
            config.set("full_auto_rec_file", file)
            logging.info(f"loaded {file}")

        file_name_label.set(file_name())

    file_name_label = tk.StringVar(value=file_name())
    ttk.Label(controls_frame, textvariable=file_name_label).grid(row=0, column=0)
    ttk.Button(controls_frame, text="Select fishy file", command=select_file).grid(row=0, column=1)
    ttk.Label(controls_frame, text="Use semi-fisher config for rest").grid(row=2, column=0, columnspan=2)

    controls_frame.pack(padx=(5, 5), pady=(5, 5))
    top.start()


def start_semifisher_config(gui: 'GUI'):
    def save():
        gui.config.set("action_key", action_key_entry.get(), False)
        gui.config.set("collect_key", collect_key_entry.get(), False)
        gui.config.set("borderless", borderless.instate(['selected']), False)
        gui.config.set("jitter", jitter.instate(['selected']), False)
        gui.config.set("sound_notification", sound.instate(['selected']), False)
        gui.config.save_config()

    def toggle_sub():
        if web.is_subbed()[0]:
            if web.unsub():
                gui._notify.set(0)
        else:
            if web.sub():
                gui._notify.set(1)

    def del_entry_key(event):
        event.widget.delete(0,"end")
        event.widget.insert(0, str(event.char))

    top = PopUp(save, gui._root, background=gui._root["background"])
    controls_frame = ttk.Frame(top)
    top.title("Config")

    ttk.Label(controls_frame, text="Notification:").grid(row=0, column=0)

    gui._notify = tk.IntVar(0)
    gui._notify_check = ttk.Checkbutton(controls_frame, command=toggle_sub, variable=gui._notify)
    gui._notify_check.grid(row=0, column=1)
    gui._notify_check['state'] = tk.DISABLED
    is_subbed = web.is_subbed()
    if is_subbed[1]:
        gui._notify_check['state'] = tk.NORMAL
        gui._notify.set(is_subbed[0])

    ttk.Label(controls_frame, text="Fullscreen: ").grid(row=1, column=0, pady=(5, 5))
    borderless = ttk.Checkbutton(controls_frame, var=tk.BooleanVar(value=config.get("borderless")))
    borderless.grid(row=1, column=1)

    ttk.Label(controls_frame, text="Action Key:").grid(row=2, column=0)
    action_key_entry = ttk.Entry(controls_frame, justify=tk.CENTER)
    action_key_entry.grid(row=2, column=1)
    action_key_entry.insert(0, config.get("action_key", "e"))
    action_key_entry.bind("<KeyRelease>", del_entry_key)

    ttk.Label(controls_frame, text="Looting Key:").grid(row=4, column=0, pady=(5, 5))
    collect_key_entry = ttk.Entry(controls_frame, justify=tk.CENTER)
    collect_key_entry.grid(row=4, column=1, pady=(5, 5))
    collect_key_entry.insert(0, config.get("collect_key", "r"))
    collect_key_entry.bind("<KeyRelease>", del_entry_key)

    ttk.Label(controls_frame, text="Sound Notification: ").grid(row=5, column=0, pady=(5, 5))
    sound = ttk.Checkbutton(controls_frame, var=tk.BooleanVar(value=config.get("sound_notification")))
    sound.grid(row=5, column=1)

    ttk.Label(controls_frame, text="Human-Like Delay: ").grid(row=6, column=0, pady=(5, 5))
    jitter = ttk.Checkbutton(controls_frame, var=tk.BooleanVar(value=config.get("jitter")))
    jitter.grid(row=6, column=1)

    controls_frame.pack(padx=(5, 5), pady=(5, 5))
    top.start()
