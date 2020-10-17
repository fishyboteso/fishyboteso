import time
import typing
from threading import Thread
from typing import Callable

import cv2
import logging

from fishy.engine.semifisher.fishing_event import FishEvent

from fishy.engine.common.window import WindowClient
from fishy.engine.semifisher.fishing_mode import FishingMode

from fishy.engine.common.IEngine import IEngine
from fishy.engine.semifisher import fishing_mode, fishing_event
from fishy.engine.semifisher.pixel_loc import PixelLoc

if typing.TYPE_CHECKING:
    from fishy.gui import GUI


class SemiFisherEngine(IEngine):
    def __init__(self, gui_ref: 'Callable[[], GUI]'):
        super().__init__(gui_ref)
        self.fishPixWindow = None

    def run(self):
        """
        Starts the fishing
        code explained in comments in detail
        """
        fishing_event.init()
        self.fishPixWindow = WindowClient(color=cv2.COLOR_RGB2HSV)

        # check for game window and stuff
        self.gui.bot_started(True)
        logging.info("Starting the bot engine, look at the fishing hole to start fishing")
        Thread(target=self._wait_and_check).start()
        while self.start:
            capture = self.fishPixWindow.get_capture()

            if capture is None:
                # if window server crashed
                self.gui.bot_started(False)
                self.toggle_start()
                continue

            self.fishPixWindow.crop = PixelLoc.val
            hue_value = capture[0][0][0]
            fishing_mode.loop(hue_value)

        logging.info("Fishing engine stopped")
        self.gui.bot_started(False)
        fishing_event.destroy()

    def _wait_and_check(self):
        time.sleep(10)
        if not FishEvent.FishingStarted and self.start:
            self.gui.show_error("Doesn't look like fishing has started\n\n"
                                "Check out #read-me-first on our discord channel to troubleshoot the issue")

    def show_pixel_vals(self):
        def show():
            freq = 0.5
            t = 0
            while t < 10.0:
                t += freq
                logging.debug(str(FishingMode.CurrentMode.label) + ":" + str(self.fishPixWindow.get_capture()[0][0]))
                time.sleep(freq)

        logging.debug("Will display pixel values for 10 seconds")
        time.sleep(5)
        Thread(target=show, args=()).start()


if __name__ == '__main__':
    logging.getLogger("").setLevel(logging.DEBUG)
    # noinspection PyTypeChecker
    fisher = SemiFisherEngine(None)
    fisher.toggle_start()

