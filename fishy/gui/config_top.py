import logging
import os
import tkinter as tk
import tkinter.ttk as ttk
import typing
from tkinter.filedialog import askopenfilename

from fishy.engine.common.event_handler import IEngineHandler
from fishy.engine.fullautofisher.mode.imode import FullAutoMode
from fishy.helper import helper

from fishy import web
from fishy.helper import helper
from fishy.helper.config import config
from fishy.helper.popup import PopUp

if typing.TYPE_CHECKING:
    from fishy.gui import GUI


def start_fullfisher_config(gui: 'GUI'):

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

    def start_calibrate():
        top.quit_top()
        config.set("calibrate", True)
        gui.engine.toggle_fullfisher()

    def mode_command():
        config.set("full_auto_mode", mode_var.get())
        edit_cb['state'] = "normal" if config.get("full_auto_mode", 0) == FullAutoMode.Recorder.value else "disable"

    def save():
        gui.config.set("spell_1", spell_1.get(), False)
        gui.config.set("spell_2", spell_2.get(), False)
        gui.config.set("spell_3", spell_3.get(), False)
        gui.config.set("spell_4", spell_4.get(), False)
        gui.config.set("spell_5", spell_5.get(), False)
        gui.config.set("walk_key", walk_key.get(), False)
        gui.config.save_config()

    def del_entry_key(event):
        event.widget.delete(0, "end")
        event.widget.insert(0, str(event.char))

    top = PopUp(save, gui._root, background=gui._root["background"])
    controls_frame = ttk.Frame(top)
    top.title("Config")

    file_name_label = tk.StringVar(value=file_name())
    mode_var = tk.IntVar(value=config.get("full_auto_mode", 0))
    edit_var = tk.IntVar(value=config.get("edit_recorder_mode", 0))
    tabout_var = tk.IntVar(value=config.get("tabout_stop", 1))
    row = 0

    ttk.Label(controls_frame, text="Calibration: ").grid(row=row, column=0, pady=(5, 0))
    ttk.Button(controls_frame, text="RUN", command=start_calibrate).grid(row=row, column=1)

    row += 1

    ttk.Label(controls_frame, text="Mode: ").grid(row=row, column=0, rowspan=2)
    ttk.Radiobutton(controls_frame, text="Player", variable=mode_var, value=FullAutoMode.Player.value, command=mode_command).grid(row=row, column=1, sticky="w", pady=(5, 0))
    row += 1
    ttk.Radiobutton(controls_frame, text="Recorder", variable=mode_var, value=FullAutoMode.Recorder.value, command=mode_command).grid(row=2, column=1, sticky="w")

    row += 1

    ttk.Label(controls_frame, text="Edit Mode: ").grid(row=row, column=0)
    edit_state = tk.NORMAL if config.get("full_auto_mode", 0) == FullAutoMode.Recorder.value else tk.DISABLED
    edit_cb = ttk.Checkbutton(controls_frame, variable=edit_var, state=edit_state, command=lambda: config.set("edit_recorder_mode", edit_var.get()))
    edit_cb.grid(row=row, column=1, pady=(5, 0))

    row += 1

    ttk.Label(controls_frame, text="Tabout Stop: ").grid(row=row, column=0)
    ttk.Checkbutton(controls_frame, variable=tabout_var, command=lambda: config.set("tabout_stop", tabout_var.get())).grid(row=row, column=1, pady=(5, 0))

    row += 1

    ttk.Label(controls_frame, text="Fishy file: ").grid(row=row, column=0, rowspan=2)
    ttk.Button(controls_frame, text="Select", command=select_file).grid(row=row, column=1, pady=(5, 0))
    row += 1
    ttk.Label(controls_frame, textvariable=file_name_label).grid(row=row, column=1, columnspan=2)

    row += 1

    ttk.Label(controls_frame, text="Move Key: ").grid(row=row, column=0, rowspan=2, pady=(5, 5))
    walk_key = ttk.Entry(controls_frame, justify=tk.CENTER)
    walk_key.grid(row=row, column=1, pady=(5, 5))
    walk_key.insert(0, config.get("walk_key", "w"))
    walk_key.bind("<KeyRelease>", del_entry_key)

    row += 1

    ttk.Label(controls_frame, text="Spell 1: ").grid(row=row, column=0, rowspan=2, pady=(5, 5))
    spell_1 = ttk.Entry(controls_frame, justify=tk.CENTER)
    spell_1.grid(row=row, column=1, pady=(5, 5))
    spell_1.insert(0, config.get("spell_1", "1"))
    spell_1.bind("<KeyRelease>", del_entry_key)

    row += 1

    ttk.Label(controls_frame, text="Spell 2: ").grid(row=row, column=0, rowspan=2, pady=(5, 5))
    spell_2 = ttk.Entry(controls_frame, justify=tk.CENTER)
    spell_2.grid(row=row, column=1, pady=(5, 5))
    spell_2.insert(0, config.get("spell_2", "2"))
    spell_2.bind("<KeyRelease>", del_entry_key)

    row += 1

    ttk.Label(controls_frame, text="Spell 3: ").grid(row=row, column=0, rowspan=2, pady=(5, 5))
    spell_3 = ttk.Entry(controls_frame, justify=tk.CENTER)
    spell_3.grid(row=row, column=1, pady=(5, 5))
    spell_3.insert(0, config.get("spell_3", "3"))
    spell_3.bind("<KeyRelease>", del_entry_key)

    row += 1

    ttk.Label(controls_frame, text="Spell 4: ").grid(row=row, column=0, rowspan=2, pady=(5, 5))
    spell_4 = ttk.Entry(controls_frame, justify=tk.CENTER)
    spell_4.grid(row=row, column=1, pady=(5, 5))
    spell_4.insert(0, config.get("spell_4", "4"))
    spell_4.bind("<KeyRelease>", del_entry_key)

    row += 1

    ttk.Label(controls_frame, text="Spell 5: ").grid(row=row, column=0, rowspan=2, pady=(5, 5))
    spell_5 = ttk.Entry(controls_frame, justify=tk.CENTER)
    spell_5.grid(row=row, column=1, pady=(5, 5))
    spell_5.insert(0, config.get("spell_5", "5"))
    spell_5.bind("<KeyRelease>", del_entry_key)

    row += 1

    ttk.Label(controls_frame, text="Use semi-fisher config for rest").grid(row=row, column=0, columnspan=2, pady=(20, 0))

    controls_frame.pack(padx=(5, 5), pady=(5, 10))
    top.start()


def start_semifisher_config(gui: 'GUI'):
    def save():
        gui.config.set("action_key", action_key_entry.get(), False)
        gui.config.set("collect_key", collect_key_entry.get(), False)
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
        event.widget.delete(0, "end")
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

    ttk.Label(controls_frame, text="Action Key:").grid(row=1, column=0)
    action_key_entry = ttk.Entry(controls_frame, justify=tk.CENTER)
    action_key_entry.grid(row=1, column=1)
    action_key_entry.insert(0, config.get("action_key", "e"))
    action_key_entry.bind("<KeyRelease>", del_entry_key)

    ttk.Label(controls_frame, text="Looting Key:").grid(row=3, column=0, pady=(5, 5))
    collect_key_entry = ttk.Entry(controls_frame, justify=tk.CENTER)
    collect_key_entry.grid(row=3, column=1, pady=(5, 5))
    collect_key_entry.insert(0, config.get("collect_key", "r"))
    collect_key_entry.bind("<KeyRelease>", del_entry_key)

    ttk.Label(controls_frame, text="Sound Notification: ").grid(row=4, column=0, pady=(5, 5))
    sound = ttk.Checkbutton(controls_frame, var=tk.BooleanVar(value=config.get("sound_notification")))
    sound.grid(row=4, column=1)

    ttk.Label(controls_frame, text="Human-Like Delay: ").grid(row=5, column=0, pady=(5, 5))
    jitter = ttk.Checkbutton(controls_frame, var=tk.BooleanVar(value=config.get("jitter")))
    jitter.grid(row=5, column=1)


    controls_frame.pack(padx=(5, 5), pady=(5, 5))
    top.start()


if __name__ == '__main__':
    from fishy.gui import GUI
    gui = GUI(lambda: IEngineHandler())
    gui.call_in_thread(lambda: start_semifisher_config(gui))
    gui.create()
