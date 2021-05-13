import logging
import os
import pickle
import time
from tkinter import ttk
from tkinter.messagebox import askyesno
import typing
from tkinter.filedialog import asksaveasfile

from fishy.helper.helper import empty_function

from fishy.helper.popup import PopUp
from playsound import playsound

from fishy import helper
from fishy.helper.config import config

if typing.TYPE_CHECKING:
    from fishy.engine.fullautofisher.engine import FullAuto
from fishy.engine.fullautofisher.mode.imode import IMode
from fishy.helper.hotkey import Key
from fishy.helper.hotkey_process import HotKey


class Recorder(IMode):
    recording_fps = 1
    mark_hole_key = Key.F8

    def __init__(self, engine: 'FullAuto'):
        self.recording = False
        self.engine = engine
        self.timeline = []

    def _mark_hole(self):
        coods = self.engine.get_coods()
        self.timeline.append(("check_fish", coods))
        playsound(helper.manifest_file("beep.wav"), False)
        logging.info("check_fish")

    def run(self):
        logging.info("starting, press LMB to mark hole")
        hk = HotKey()
        hk.start_process(self._mark_hole)

        self.timeline = []

        while self.engine.start:
            start_time = time.time()
            coods = None
            while not coods:
                coods = self.engine.get_coods()
            self.timeline.append(("move_to", (coods[0], coods[1])))

            time_took = time.time() - start_time
            if time_took <= Recorder.recording_fps:
                time.sleep(Recorder.recording_fps - time_took)
            else:
                logging.warning("Took too much time to record")

        hk.stop()
        self._ask_to_save()

    def _open_save_popup(self):
        top = PopUp(empty_function, self.engine.get_gui()._root, background=self.engine.get_gui()._root["background"])
        controls_frame = ttk.Frame(top)
        top.title("Save Recording?")

        button = [-1]

        def button_pressed(_button):
            button[0] = _button
            top.quit_top()

        ttk.Label(controls_frame, text="Do you want to save the recording?").grid(row=0, column=0, columnspan=3)

        _overwrite = "normal" if config.get("full_auto_rec_file") else "disable"
        ttk.Button(controls_frame, text="Overwrite", command=lambda: button_pressed(0), state=_overwrite).grid(row=1, column=0)
        ttk.Button(controls_frame, text="Save As", command=lambda: button_pressed(1)).grid(row=1, column=1)
        ttk.Button(controls_frame, text="Cancel", command=lambda: button_pressed(2)).grid(row=1, column=2)

        controls_frame.pack(padx=(5, 5), pady=(5, 5))
        top.start()

        return button[0]

    def _ask_to_save(self):
        def func():
            _file = None
            files = [('Fishy File', '*.fishy')]

            while True:
                button = self._open_save_popup()
                if button == 0 and config.get("full_auto_rec_file"):
                    return open(config.get("full_auto_rec_file"), 'wb')

                if button == 1:
                    _file = asksaveasfile(mode='wb', filetypes=files, defaultextension=files)
                    if _file:
                        return _file

                if button == 2:
                    return None

        file: typing.BinaryIO = self.engine.get_gui().call_in_thread(func, block=True)
        if not file:
            return

        data = {"full_auto_path": self.timeline}
        pickle.dump(data, file)
        config.set("full_auto_rec_file", file.name)
        logging.info(f"saved {os.path.basename(file.name)} recording, and loaded it in player")
        file.close()
