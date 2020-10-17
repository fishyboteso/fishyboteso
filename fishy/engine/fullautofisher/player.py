import json
import logging
import pickle
import time
from threading import Thread
from tkinter.filedialog import asksaveasfile, askopenfile

from fishy.engine.fullautofisher.engine import FullAuto

from fishy.helper import hotkey, helper
from fishy.helper.hotkey import Key


class Player:
    def __init__(self, engine: 'FullAuto'):
        self.recording = False
        self.engine = engine
        self.timeline = []
        self.hole_complete_flag = False
        self.start_moving_flag = False

    def _mark_hole(self):
        coods = self.engine.get_coods()
        self.timeline.append(("check_fish", coods))

    def _start_moving(self):
        self.start_moving_flag = True

    def _stop_recording(self):
        self.recording = False

    def _hole_complete_callback(self, e):
        if e == "idle":
            self.hole_complete_flag = True

    def start_route(self):
        file = askopenfile(mode='rb', filetypes=[('Python Files', '*.fishy')])
        if not file:
            logging.error("file not selected")
            return
        data = pickle.load(file)
        file.close()
        print(data)
        if "full_auto_path" not in data:
            logging.error("incorrect file")
            return
        self.timeline = data["full_auto_path"]

        # wait until f8 is pressed
        logging.info("press f8 to start")
        self.start_moving_flag = False
        hotkey.set_hotkey(Key.F8, self._start_moving)
        helper.wait_until(lambda: self.start_moving_flag)

        logging.info("starting")
        for action in self.timeline:
            if action[0] == "move_to":
                self.engine.move_to(action[1])
                logging.info("moved")
            elif action[0] == "check_fish":
                self.engine.move_to(action[1])
                self.engine.rotate_to(action[1][2])
                # scan for fish hole
                logging.info("scanning")
                if self.engine.look_for_hole():
                    self.hole_complete_flag = False
                    helper.wait_until(lambda: self.hole_complete_flag)
                # if found start fishing and wait for hole to complete
                # contine when hole completes

