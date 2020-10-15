import json
import logging
import time
from threading import Thread
from tkinter.filedialog import asksaveasfile, askopenfile

from fishy.engine.fullautofisher.engine import FullAuto

from fishy.helper import hotkey, helper
from fishy.helper.hotkey import Key


class Player:
    def __init__(self, engine: FullAuto):
        self.recording = False
        self.engine = engine
        self.timeline = []
        self.hole_complete_flag = False

    def _mark_hole(self):
        coods = self.engine.get_coods()
        self.timeline.append(("check_fish", coods))

    def _stop_recording(self):
        self.recording = False

    def _hole_complete_callback(self, e):
        if e == "idle":
            self.hole_complete_flag = True

    def start(self):
        Thread(target=self.start_route).start()

    def start_route(self):
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
                if self.engine.look_for_hole():
                    self.hole_complete_flag = False
                    helper.wait_until(lambda: self.hole_complete_flag)
                # if found start fishing and wait for hole to complete
                # contine when hole completes

