import logging
import os
import typing
from tkinter.filedialog import askopenfilename

from fishy.helper import helper

from fishy import web

from tkinter import *
from tkinter.ttk import *

from fishy.helper.config import config
from fishy.helper.popup import PopUp

if typing.TYPE_CHECKING:
    from fishy.gui import GUI


def start_fullfisher_config(gui: 'GUI'):
    top = PopUp(helper.empty_function, gui._root, background=gui._root["background"])
    controls_frame = Frame(top)
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

    file_name_label = StringVar(value=file_name())
    Label(controls_frame, textvariable=file_name_label).grid(row=0, column=0)
    Button(controls_frame, text="Select fishy file", command=select_file).grid(row=0, column=1)
    Label(controls_frame, text="Use semi-fisher config for rest").grid(row=2, column=0, columnspan=2)

    controls_frame.pack(padx=(5, 5), pady=(5, 5))
    top.start()


def start_semifisher_config(gui: 'GUI'):
    def save():
        gui.config.set("action_key", action_key_entry.get(), False)
        gui.config.set("collect_key", collect_key_entry.get(), False)
        gui.config.set("collect_allow_auto", collect_allow_auto.instate(['selected']), False)
        gui.config.set("borderless", borderless.instate(['selected']), False)
        gui.config.set("jitter", jitter.instate(['selected']), False)
        gui.config.set("sound_notification", sound.instate(['selected']), False)
        gui.config.save_config()

    def toggle_sub():
        if web.is_subbed(config.get("uid"))[0]:
            if web.unsub(config.get("uid")):
                gui._notify.set(0)
        else:
            if web.sub(config.get("uid")):
                gui._notify.set(1)
                
    def toggle_collect():
        gui.config.set("collect_allow_auto", collect_allow_auto.instate(['selected']), False)
        collect_key_entry['state'] = NORMAL if config.get("collect_allow_auto") else DISABLED

    top = PopUp(save, gui._root, background=gui._root["background"])
    controls_frame = Frame(top)
    top.title("Config")

    Label(controls_frame, text="Notification:").grid(row=0, column=0)

    gui._notify = IntVar(0)
    gui._notify_check = Checkbutton(controls_frame, command=toggle_sub, variable=gui._notify)
    gui._notify_check.grid(row=0, column=1)
    gui._notify_check['state'] = DISABLED
    is_subbed = web.is_subbed(config.get('uid'))
    if is_subbed[1]:
        gui._notify_check['state'] = NORMAL
        gui._notify.set(is_subbed[0])

    Label(controls_frame, text="Fullscreen: ").grid(row=1, column=0, pady=(5, 5))
    borderless = Checkbutton(controls_frame, var=BooleanVar(value=config.get("borderless")))
    borderless.grid(row=1, column=1)

    Label(controls_frame, text="Action Key:").grid(row=2, column=0)
    action_key_entry = Entry(controls_frame, justify=CENTER)
    action_key_entry.grid(row=2, column=1)
    action_key_entry.insert(0, config.get("action_key", "e"))


    Label(controls_frame, text="Auto-Looting: ").grid(row=3, column=0, pady=(15, 0))
    collect_allow_auto = Checkbutton(controls_frame, command=toggle_collect, var=BooleanVar(value=config.get("collect_allow_auto")))
    collect_allow_auto.grid(row=3, column=1, pady=(15, 0))
    
    Label(controls_frame, text="Looting Key:").grid(row=4, column=0, pady=(0, 15))
    collect_key_entry = Entry(controls_frame, justify=CENTER)
    collect_key_entry.grid(row=4, column=1, pady=(0, 15))
    collect_key_entry.insert(0, config.get("collect_key", "r"))
    collect_key_entry['state'] = NORMAL if config.get("collect_allow_auto") else DISABLED

    Label(controls_frame, text="Sound Notification: ").grid(row=5, column=0, pady=(5, 5))
    sound = Checkbutton(controls_frame, var=BooleanVar(value=config.get("sound_notification")))
    sound.grid(row=5, column=1)

    Label(controls_frame, text="Human-Like Delay: ").grid(row=4, column=0, pady=(5, 5))
    jitter = Checkbutton(controls_frame, var=BooleanVar(value=config.get("jitter")))
    jitter.grid(row=4, column=1)

    controls_frame.pack(padx=(5, 5), pady=(5, 5))
    top.start()
