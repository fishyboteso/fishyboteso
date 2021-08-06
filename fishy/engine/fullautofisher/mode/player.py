import logging
import math
import pickle
import time
from pprint import pprint

import typing
from threading import Thread

from fishy.engine.fullautofisher.mode.imode import IMode
from fishy.engine.semifisher import fishing_event, fishing_mode
from fishy.engine.semifisher.fishing_mode import FishingMode, State
from fishy.helper.helper import log_raise, wait_until, kill_thread

if typing.TYPE_CHECKING:
    from fishy.engine.fullautofisher.engine import FullAuto

from fishy.helper import helper
from fishy.helper.config import config


def get_rec_file():
    file = config.get("full_auto_rec_file")

    if not file:
        logging.error("Please select a fishy file first from config")
        return None

    file = open(file, 'rb')
    data = pickle.load(file)
    file.close()
    if "full_auto_path" not in data:
        logging.error("invalid file")
        return None
    return data["full_auto_path"]


def find_nearest(timeline, current):
    """
    :param timeline: recording timeline
    :param current: current coord
    :return: Tuple[index, distance, target_coord]
    """
    distances = [(i, math.sqrt((target[0] - current[0]) ** 2 + (target[1] - current[1]) ** 2), target)
                 for i, (command, target) in enumerate(timeline) if command == "move_to"]
    return min(distances, key=lambda d: d[1])


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
            time.sleep(0.1)
        logging.info("player stopped")

    def _init(self):
        self.timeline = get_rec_file()
        if not self.timeline:
            log_raise("data not found, can't start")
        logging.info("starting player")

        coords = self.engine.get_coords()
        if not coords:
            log_raise("QR not found")

        self.i = find_nearest(self.timeline, coords)[0]

    def _loop(self):
        action = self.timeline[self.i]

        fishing_mode.subscribers.append(self._hole_complete_callback)
        fishing_event.subscribe()
        if FishingMode.CurrentMode != State.FIGHT:
            if action[0] == "move_to":
                if not self.engine.move_to(action[1]):
                    return
            elif action[0] == "check_fish":
                if not self.engine.move_to(action[1]):
                    return

                if not self.engine.rotate_to(action[1][2]):
                    return
        # scan for fish hole
        logging.info("scanning")
        # if found start fishing and wait for hole to complete
        if self.engine.look_for_hole():
            logging.info("starting fishing")
            self.hole_complete_flag = False
            helper.wait_until(lambda: self.hole_complete_flag or not self.engine.start)
            self.engine.rotate_back()
        elif FishingMode.CurrentMode == State.FIGHT:
            logging.info("busy now...")
        else:
            logging.info("no hole found")
    

        # continue when hole completes
        fishing_mode.subscribers.remove(self._hole_complete_callback)
        fishing_event.unsubscribe()

        self.next()

    def next(self):
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
