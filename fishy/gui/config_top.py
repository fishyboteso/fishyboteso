import logging
import os
import tempfile
import typing
from zipfile import ZipFile

from google.auth.transport import requests

from fishy import web
from fishy.gui.notification import _give_notification_link

from tkinter import *
from tkinter.ttk import *

from fishy.helper.config import config
from fishy.helper.downloader import download_file_from_google_drive
from fishy.helper.popup import PopUp

if typing.TYPE_CHECKING:
    from fishy.gui import GUI


def start_fullfisher_config(gui: 'GUI'):
    def save():
        gui.config.set("tesseract_dir", tesseract_entry.get(), False)
        gui.config.save_config()

    top = PopUp(save, gui._root, background=gui._root["background"])
    controls_frame = Frame(top)
    top.title("Config")

    Label(controls_frame, text="Tesseract Directory:").grid(row=0, column=0)
    tesseract_entry = Entry(controls_frame, justify=CENTER)
    tesseract_entry.insert(0, config.get("tesseract_dir", ""))
    tesseract_entry.grid(row=0, column=1)

    controls_frame.pack(padx=(5, 5), pady=(5, 5))
    top.start()


def start_semifisher_config(gui: 'GUI'):
    def save():
        gui.config.set("action_key", action_key_entry.get(), False)
        gui.config.set("borderless", borderless.instate(['selected']), False)
        gui.config.set("sound_notification", sound.instate(['selected']), False)
        gui.config.save_config()

    top = PopUp(save, gui._root, background=gui._root["background"])
    controls_frame = Frame(top)
    top.title("Config")

    Label(controls_frame, text="Notification:").grid(row=0, column=0)

    gui._notify = IntVar(0)
    gui._notify_check = Checkbutton(controls_frame, command=lambda: _give_notification_link(gui),
                                    variable=gui._notify)
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

    Label(controls_frame, text="Sound Notification: ").grid(row=3, column=0, pady=(5, 5))
    sound = Checkbutton(controls_frame, var=BooleanVar(value=config.get("sound_notification")))
    sound.grid(row=3, column=1)

    controls_frame.pack(padx=(5, 5), pady=(5, 5))
    top.start()
