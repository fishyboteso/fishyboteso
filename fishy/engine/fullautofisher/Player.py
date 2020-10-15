import json
import logging
import time
from tkinter.filedialog import asksaveasfile, askopenfile

from fishy.engine.fullautofisher.engine import FullAuto

from fishy.helper import hotkey
from fishy.helper.hotkey import Key


class Player:
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
        file = askopenfile(mode='r', filetypes=[('Python Files', '*.py')])
        if not file:
            logging.error("file not selected")
            return
        data = json.load(file)
        if "full_auto_path" not in data:
            logging.error("incorrect file")
            return

        self.timeline = data["full_auto_path"]

        for action in self.timeline:
            if action == "move_to":
                self.engine.move_to(action[1])
            elif action == "check_fish":
                self.engine.move_to(action[1])
                self.engine.rotate_to(action[1][2])
                # scan for fish hole
                # if found start fishing and wait for hole to complete
                # contine when hole completes

        logging.info("f7 for marking hole, f8 to stop recording")
        hotkey.set_hotkey(Key.F7, self._mark_hole)
        hotkey.set_hotkey(Key.F8, self._stop_recording)

        self.recording = True
        self.timeline = []

        while self.recording:
            start_time = time.time()
            coods = self.engine.get_coods()
            self.timeline.append(("goto", (coods[0], coods[1])))

            time_took = time.time() - start_time
            if time_took <= Recorder.recording_fps:
                time.sleep(Recorder.recording_fps - time_took)
            else:
                logging.warning("Took too much time to record")

        file = None
        while not file:
            file = asksaveasfile(mode='wb', filetypes=[('Fishy File', '*.fishy')])
        data = {"full_auto_path": self.timeline}
        json.dump(data, file)
        file.close()

