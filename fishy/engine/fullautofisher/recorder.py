import logging
import pickle
import time
from tkinter.filedialog import asksaveasfile

from fishy.engine.fullautofisher.engine import FullAuto

from fishy.helper import hotkey
from fishy.helper.hotkey import Key


class Recorder:
    recording_fps = 1

    def __init__(self, engine: FullAuto):
        self.recording = False
        self.engine = engine
        self.timeline = []

    def _mark_hole(self):
        coods = self.engine.get_coods()
        self.timeline.append(("check_fish", coods))

    def _stop_recording(self):
        self.recording = False

    def start_recording(self):
        logging.info("f7 for marking hole, f8 to stop recording")
        hotkey.set_hotkey(Key.F7, self._mark_hole)
        hotkey.set_hotkey(Key.F8, self._stop_recording)

        self.recording = True
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

        files = [('Fishy File', '*.fishy')]
        file = None
        while not file:
            file = asksaveasfile(mode='wb', filetypes=files, defaultextension=files)
        data = {"full_auto_path": self.timeline}
        print(data)
        pickle.dump(data, file)
        file.close()

