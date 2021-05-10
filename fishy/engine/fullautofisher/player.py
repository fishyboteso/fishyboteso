import logging
import pickle
from pprint import pprint

from fishy.engine.fullautofisher.engine import FullAuto, State
from fishy.engine.semifisher import fishing_event, fishing_mode
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


class Player:
    def __init__(self, engine: 'FullAuto'):
        self.recording = False
        self.engine = engine
        self.hole_complete_flag = False
        self.start_moving_flag = False

    def toggle_move(self):
        if FullAuto.state != State.PLAYING and FullAuto.state != State.NONE:
            return

        self.start_moving_flag = not self.start_moving_flag
        if self.start_moving_flag:
            self._start_route()
        else:
            logging.info("Waiting for the last action to finish...")

    def _hole_complete_callback(self, e):
        if e == fishing_event.State.IDLE:
            self.hole_complete_flag = True

    def _start_route(self):
        timeline = _get_rec_file()
        if not timeline:
            logging.log("data not found, can't start")
            return

        FullAuto.state = State.PLAYING
        logging.info("starting to move")

        forward = True
        i = 0
        while self.start_moving_flag:
            action = timeline[i]

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
            if i >= len(timeline):
                forward = False
                i = len(timeline) - 1
            elif i < 0:
                forward = True
                i = 0

        logging.info("stopped")
        FullAuto.state = State.NONE
