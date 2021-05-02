import logging
import os
import pickle
import time
from pprint import pprint
from tkinter.filedialog import asksaveasfile

import typing

from fishy.helper.config import config
from playsound import playsound

from fishy import helper

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

        def func():
            _file = None
            files = [('Fishy File', '*.fishy')]
            while not _file:
                _file = asksaveasfile(mode='wb', filetypes=files, defaultextension=files)

            return _file

        file: typing.BinaryIO = self.engine.get_gui().call_in_thread(func, block=True)
        data = {"full_auto_path": self.timeline}
        pickle.dump(data, file)
        config.set("full_auto_rec_file", file.name)
        logging.info(f"saved {os.path.basename(file.name)} recording, and loaded it in player")
        file.close()

