import logging
import math
import pickle
from pprint import pprint

import typing
from threading import Thread

from fishy.engine.fullautofisher.mode.imode import IMode
from fishy.engine.semifisher import fishing_event, fishing_mode
from fishy.helper.helper import log_raise, wait_until, kill_thread

if typing.TYPE_CHECKING:
    from fishy.engine.fullautofisher.engine import FullAuto

from fishy.helper import helper
from fishy.helper.config import config


def _get_rec_file():
    file = config.get("full_auto_rec_file")

    if not file:
        logging.error("Please select a fishy file first from config")
        return None

    file = open(file, 'rb')
    data = pickle.load(file)
    file.close()
    pprint(data)
    if "full_auto_path" not in data:
        logging.error("invalid file")
        return None
    return data["full_auto_path"]


class Player(IMode):
    def __init__(self, engine: 'FullAuto'):
        self.recording = False
        self.engine = engine
        self.hole_complete_flag = False
        self.start_moving_flag = False
        self.i = 0
        self.forward = True
        self.timeline = None

    def run(self):
        self._init()
        while self.engine.start:
            self._loop()
        logging.info("player stopped")

    def _init(self):
        self.timeline = _get_rec_file()
        if not self.timeline:
            log_raise("data not found, can't start")
        logging.info("starting player")

        self.i = self._closest_point()

    def _closest_point(self):
        current = self.engine.get_coods()
        distances = [(i, math.sqrt((target[0] - current[0]) ** 2 + (target[1] - current[1]) ** 2))
                     for i, (command, target) in enumerate(self.timeline) if command == "move_to"]
        return min(distances, key=lambda d: d[1])[0]

    def _loop(self):
        action = self.timeline[self.i]

        if action[0] == "move_to":
            self.engine.move_to(action[1])
        elif action[0] == "check_fish":
            self.engine.move_to(action[1])
            self.engine.rotate_to(action[1][2])
            fishing_event.subscribe()
            fishing_mode.subscribers.append(self._hole_complete_callback)
            # scan for fish hole
            logging.info("scanning")
            # if found start fishing and wait for hole to complete
            if self.engine.look_for_hole():
                logging.info("starting fishing")
                self.hole_complete_flag = False
                helper.wait_until(lambda: self.hole_complete_flag or not self.engine.start)
                self.engine.rotate_back()
            else:
                logging.info("no hole found")
            # continue when hole completes
            fishing_event.unsubscribe()
            fishing_mode.subscribers.remove(self._hole_complete_callback)

        self.i += 1 if self.forward else -1
        if self.i >= len(self.timeline):
            self.forward = False
            self.i = len(self.timeline) - 1
        elif self.i < 0:
            self.forward = True
            self.i = 0

    def _hole_complete_callback(self, e):
        if e == fishing_event.State.IDLE:
            self.hole_complete_flag = True
