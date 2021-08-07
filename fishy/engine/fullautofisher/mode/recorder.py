import logging
import os
import pickle
import time
import tkinter as tk
from tkinter import ttk
from typing import List, Optional
import typing
from tkinter.filedialog import asksaveasfile

from fishy.engine.fullautofisher.mode import player
from fishy.helper import helper

from fishy.helper.helper import empty_function, log_raise
from fishy.helper.hotkey.process import Key

from fishy.helper.popup import PopUp
from playsound import playsound

from fishy.helper.config import config

if typing.TYPE_CHECKING:
    from fishy.engine.fullautofisher.engine import FullAuto
from fishy.engine.fullautofisher.mode.imode import IMode
from fishy.helper.hotkey.hotkey_process import HotKey, hotkey


class Recorder(IMode):
    recording_fps = 1

    def __init__(self, engine: 'FullAuto'):
        self.recording = False
        self.engine = engine
        self.timeline = []

    def _mark_hole(self):
        coords = self.engine.get_coords()
        if not coords:
            logging.warning("QR not found, couldn't record hole")
            return
        self.timeline.append(("check_fish", coords))
        logging.info("check_fish")

    def _mark_waypoint(self):
        coords = self.engine.get_coords()

        # time_took = time.time() - start_time
        # if time_took <= Recorder.recording_fps:
        #     time.sleep(Recorder.recording_fps - time_took)
        # else:
        #     logging.warning("Took too much time to record")

        # if config.get("edit_recorder_mode"):
        #     logging.info("moving to nearest coord in recording")

        #     # todo allow the user the chance to wait for qr
        #     coords = self.engine.get_coords()
        #     if not coords:
        #         log_raise("QR not found")

        #     end = player.find_nearest(old_timeline, coords)
        #     self.engine.move_to(end[2])
        #     part1 = old_timeline[:start_from[0]]
        #     part2 = old_timeline[end[0]:]
        #     self.timeline = part1 + self.timeline + part2
        if not coords:
            logging.warning("QR not found, couldn't record hole")
            return
        self.timeline.append(("move_to", (coords[0], coords[1])))
        logging.info("move_to")

    def run(self):
        old_timeline: Optional[List] = None
        start_from = None

        if config.get("edit_recorder_mode"):
            logging.info("moving to nearest coord in recording")

            old_timeline = player.get_rec_file()
            if not old_timeline:
                log_raise("Edit mode selected, but no fishy file selected")

            coords = self.engine.get_coords()
            if not coords:
                log_raise("QR not found")

            start_from = player.find_nearest(old_timeline, coords)
            if not self.engine.move_to(start_from[2]):
                log_raise("QR not found")
        else:
            pass

        self.timeline = []

        logging.info("starting...")
        logging.info("""press LMB to mark hole
            or RMB to mark a waypoint""")
        while self.engine.start:
            hotkey.hook(Key.LMB, self._mark_hole)
            hotkey.hook(Key.RMB, self._mark_waypoint)
        else:
            hotkey.free(Key.LMB)
            hotkey.free(Key.RMB)
        
        self._ask_to_save()

    def _open_save_popup(self):
        top = PopUp(empty_function, self.engine.get_gui()._root, background=self.engine.get_gui()._root["background"])
        controls_frame = ttk.Frame(top)
        top.title("Save Recording?")

        button = [-1]

        def button_pressed(_button):
            button[0] = _button
            top.quit_top()

        selected_text = f"\n\nSelected: {os.path.basename(config.get('full_auto_rec_file'))}" if config.get('edit_recorder_mode') else ""
        ttk.Label(controls_frame, text=f"Do you want to save the recording?{selected_text}").grid(row=0, column=0, columnspan=3, pady=(0, 5))

        _overwrite = tk.NORMAL if config.get("edit_recorder_mode") else tk.DISABLED
        ttk.Button(controls_frame, text="Overwrite", command=lambda: button_pressed(0), state=_overwrite).grid(row=1, column=0, pady=(5, 0))
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



