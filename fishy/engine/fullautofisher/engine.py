import logging
import math
import time
from threading import Thread

from fishy.engine.common import qr_detection
from pynput import keyboard, mouse

from fishy.engine import SemiFisherEngine
from fishy.engine.common.IEngine import IEngine
from fishy.engine.common.window import WindowClient
from fishy.engine.fullautofisher.mode.calibrator import Calibrator
from fishy.engine.fullautofisher.mode.imode import FullAutoMode
from fishy.engine.fullautofisher.mode.player import Player
from fishy.engine.fullautofisher.mode.recorder import Recorder
from fishy.engine.semifisher import fishing_mode
from fishy.engine.semifisher.fishing_mode import FishingMode
from fishy.helper.config import config
from fishy.helper.helper import wait_until, is_eso_active, sign, print_exc

mse = mouse.Controller()
kb = keyboard.Controller()


class FullAuto(IEngine):
    rotate_by = 30

    def __init__(self, gui_ref):
        from fishy.engine.fullautofisher.test import Test

        super().__init__(gui_ref)
        self.name = "FullAuto"
        self._curr_rotate_y = 0

        self.fisher = SemiFisherEngine(None)
        self.calibrator = Calibrator(self)
        self.test = Test(self)
        self.show_crop = False

        self.mode = None

    def run(self):
        self.mode = None
        if config.get("calibrate", False):
            self.mode = Calibrator(self)
        elif FullAutoMode(config.get("full_auto_mode", 0)) == FullAutoMode.Player:
            self.mode = Player(self)
        elif FullAutoMode(config.get("full_auto_mode", 0)) == FullAutoMode.Recorder:
            self.mode = Recorder(self)
        else:
            logging.error("not a valid mode selected")
            return

        # block thread until game window becomes active
        if not is_eso_active():
            logging.info("Waiting for eso window to be active...")
            wait_until(lambda: is_eso_active() or not self.start)
            if self.start:
                logging.info("starting in 2 secs...")
                time.sleep(2)

        if not (type(self.mode) is Calibrator) and not self.calibrator.all_calibrated():
            logging.error("you need to calibrate first")
            return

        if not qr_detection.get_values(self.window):
            logging.error("FishyQR not found, if its not hidden, try to drag it around, "
                          "or increase/decrease its size and try again\nStopping engine...")
            return

        if config.get("tabout_stop", 1):
            self.stop_on_inactive()

        # noinspection PyBroadException
        try:
            self.mode.run()
        except Exception:
            logging.error("exception occurred while running full auto mode")
            print_exc()

    def start_show(self):
        def func():
            while self.start and WindowClient.running():
                self.window.show(self.show_crop)
        Thread(target=func).start()

    def stop_on_inactive(self):
        def func():
            logging.debug("stop on inactive started")
            wait_until(lambda: not is_eso_active() or not self.start)
            if self.start and not is_eso_active():
                self.turn_off()
            logging.debug("stop on inactive stopped")
        Thread(target=func).start()

    def get_coords(self):
        """
        There is chance that this function give None instead of a QR.
        Need to handle manually
        todo find a better way of handling None: switch from start bool to state which knows
        todo its waiting for qr which doesn't block the engine when commanded to close
        """
        values = qr_detection.get_values(self.window)
        return values[:3] if values else None

    def move_to(self, target) -> bool:
        current = self.get_coords()
        if not current:
            return False

        logging.debug(f"Moving from {(current[0], current[1])} to {target}")
        move_vec = target[0] - current[0], target[1] - current[1]

        dist = math.sqrt(move_vec[0] ** 2 + move_vec[1] ** 2)
        logging.debug(f"distance: {dist}")
        if dist < 5e-05:
            logging.debug("distance very small skipping")
            return True

        target_angle = math.degrees(math.atan2(-move_vec[1], move_vec[0])) + 90
        from_angle = current[2]

        if not self.rotate_to(target_angle, from_angle):
            return False

        walking_time = dist / self.calibrator.move_factor
        logging.debug(f"walking for {walking_time}")
        kb.press('w')
        time.sleep(walking_time)
        kb.release('w')
        logging.debug("done")
        # todo: maybe check if it reached the destination before returning true?
        return True

    def rotate_to(self, target_angle, from_angle=None) -> bool:
        if from_angle is None:
            coords = self.get_coords()
            if not coords:
                return False
            _, _, from_angle = coords

        if target_angle < 0:
            target_angle = 360 + target_angle
        while target_angle > 360:
            target_angle -= 360
        logging.debug(f"Rotating from {from_angle} to {target_angle}")

        angle_diff = target_angle - from_angle

        if abs(angle_diff) > 180:
            angle_diff = (360 - abs(angle_diff)) * sign(angle_diff) * -1

        rotate_times = int(angle_diff / self.calibrator.rot_factor) * -1

        logging.debug(f"rotate_times: {rotate_times}")

        for _ in range(abs(rotate_times)):
            mse.move(sign(rotate_times) * FullAuto.rotate_by * -1, 0)
            time.sleep(0.05)

        return True

    def look_for_hole(self) -> bool:
        valid_states = [fishing_mode.State.LOOKING, fishing_mode.State.FISHING]
        _hole_found_flag = FishingMode.CurrentMode in valid_states

        # if vertical movement is disabled
        if not config.get("look_for_hole", 1):
            return _hole_found_flag

        t = 0
        while not _hole_found_flag and t <= 2.5:
            direction = -1 if t > 1.25 else 1
            mse.move(0, FullAuto.rotate_by*direction)
            time.sleep(0.05)
            t += 0.05
            _hole_found_flag = FishingMode.CurrentMode in valid_states

        self._curr_rotate_y = t
        return _hole_found_flag

    def rotate_back(self):
        while self._curr_rotate_y > 0.01:
            mse.move(0, -FullAuto.rotate_by)
            time.sleep(0.05)
            self._curr_rotate_y -= 0.05


if __name__ == '__main__':
    # noinspection PyTypeChecker
    bot = FullAuto(None)
    bot.toggle_start()
