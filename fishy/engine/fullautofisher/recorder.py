import logging
import pickle
import time
from pprint import pprint
from tkinter.filedialog import asksaveasfile

from fishy.engine.fullautofisher.engine import FullAuto, State

from fishy.helper.hotkey import Key
from fishy.helper.hotkey_process import HotKey


class Recorder:
    recording_fps = 1
    mark_hole_key = Key.F8

    def __init__(self, engine: FullAuto):
        self.recording = False
        self.engine = engine
        self.timeline = []

    def _mark_hole(self):
        coods = self.engine.get_coods()
        self.timeline.append(("check_fish", coods))
        logging.info("check_fish")

    def toggle_recording(self):
        if FullAuto.state != State.RECORDING and FullAuto.state != State.NONE:
            return

        self.recording = not self.recording
        if self.recording:
            self._start_recording()

    def _start_recording(self):
        FullAuto.state = State.RECORDING
        logging.info("starting, press f8 to mark hole")
        hk = HotKey()
        hk.start_process(self._mark_hole)

        self.timeline = []

        while self.recording:
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

        file = self.engine.get_gui().call_in_thread(func, block=True)
        data = {"full_auto_path": self.timeline}
        pprint(data)
        pickle.dump(data, file)
        file.close()
        FullAuto.state = State.NONE

