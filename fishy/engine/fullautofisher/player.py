import logging
import pickle
from pprint import pprint

from fishy.engine.semifisher import fishing_event, fishing_mode

from fishy.engine.fullautofisher.engine import FullAuto

from fishy.helper import hotkey, helper
from fishy.helper.config import config
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
        self.start_moving_flag = not self.start_moving_flag

    def _stop_recording(self):
        self.recording = False

    def _hole_complete_callback(self, e):
        if e == fishing_event.State.IDLE:
            self.hole_complete_flag = True

    def start_route(self):
        file = config.get("full_auto_rec_file")

        if not file:
            logging.error("Please select a fishy file first from config")
            return

        file = open(file, 'rb')
        data = pickle.load(file)
        file.close()
        pprint(data)
        if "full_auto_path" not in data:
            logging.error("invalid file")
            return
        self.timeline = data["full_auto_path"]

        # wait until f8 is pressed
        logging.info("press f8 to start")

        self.start_moving_flag = False
        hotkey.set_hotkey(Key.F8, self._start_moving)
        helper.wait_until(lambda: self.start_moving_flag)

        logging.info("starting, press f8 to stop")
        forward = True
        i = 0
        while self.start_moving_flag:
            action = self.timeline[i]

            if action[0] == "move_to":
                self.engine.move_to(action[1])
            elif action[0] == "check_fish":
                self.engine.move_to(action[1])
                self.engine.rotate_to(action[1][2])
                fishing_event.subscribe()
                fishing_mode.subscribers.append(self._hole_complete_callback)
                # scan for fish hole
                logging.info("scanning")
                if self.engine.look_for_hole():
                    logging.info("starting fishing")
                    self.hole_complete_flag = False
                    helper.wait_until(lambda: self.hole_complete_flag or not self.start_moving_flag)
                    self.engine.rotate_back()
                else:
                    logging.info("no hole found")
                # if found start fishing and wait for hole to complete
                # contine when hole completes
                fishing_event.unsubscribe()
                fishing_mode.subscribers.remove(self._hole_complete_callback)

            i += 1 if forward else -1
            if i >= len(self.timeline):
                forward = False
                i = len(self.timeline) - 1
            elif i < 0:
                forward = True
                i = 0

        logging.info("stopped")
