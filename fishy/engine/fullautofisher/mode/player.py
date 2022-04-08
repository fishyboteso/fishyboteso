import logging
import math
import pickle
import time

import typing

from fishy.engine.fullautofisher.mode.imode import IMode
from fishy.engine.semifisher import fishing_event, fishing_mode

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
        if not self._init():
            return

        while self.engine.start:
            self._loop()
            time.sleep(0.1)

        logging.info("player stopped")

    def _init(self) -> bool:
        self.timeline = get_rec_file()
        if not self.timeline:
            logging.error("data not found, can't start")
            return False

        coords = self.engine.get_coords()
        if not coords:
            logging.error("QR not found")
            return False

        self.i = find_nearest(self.timeline, coords)[0]
        logging.info("starting player")
        return True

    def _loop(self):
        action = self.timeline[self.i]

        if action[0] == "move_to":
            if not self.engine.move_to(action[1]):
                return
        elif action[0] == "check_fish":
            if not self.engine.move_to(action[1]):
                return

            if not self.engine.rotate_to(action[1][2]):
                return

            self.engine.fisher.turn_on()
            helper.wait_until(lambda: self.engine.fisher.first_loop_done)
            # scan for fish hole
            logging.info("scanning")
            # if found start fishing and wait for hole to complete
            if self.engine.look_for_hole():
                logging.info("starting fishing")
                fishing_mode.subscribers.append(self._hole_complete_callback)
                self.hole_complete_flag = False
                helper.wait_until(lambda: self.hole_complete_flag or not self.engine.start)
                fishing_mode.subscribers.remove(self._hole_complete_callback)

                self.engine.rotate_back()
            else:
                logging.info("no hole found")
            # continue when hole completes
            self.engine.fisher.turn_off()

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
