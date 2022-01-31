import logging
import time
import typing
from threading import Thread
from typing import Callable, Optional

import cv2
from fishy.engine.semifisher.fishing_mode import FishingMode

from fishy.helper.helper import log_raise
from playsound import playsound

from fishy.engine.common.IEngine import IEngine
from fishy.engine.common.qr_detection import get_qr_location, get_values_from_image, image_pre_process
from fishy.engine.common.window import WindowClient
from fishy.engine.semifisher import fishing_event, fishing_mode
from fishy.engine.semifisher.fishing_event import FishEvent
from fishy.helper import helper
from fishy.helper.luaparser import sv_color_extract

if typing.TYPE_CHECKING:
    from fishy.gui import GUI


class SemiFisherEngine(IEngine):
    def __init__(self, gui_ref: Optional['Callable[[], GUI]']):
        super().__init__(gui_ref)
        self.window = None

    def run(self):
        """
        Starts the fishing
        code explained in comments in detail
        """
        self.window = WindowClient(color=cv2.COLOR_RGB2GRAY, show_name="semifisher debug")

        if self.get_gui:
            logging.info("Starting the bot engine, look at the fishing hole to start fishing")
            Thread(target=self._wait_and_check).start()

        self.window.crop = get_qr_location(self.window.get_capture())
        if not self.window.crop:
            logging.error("FishyQR not found, try to drag it around and try again")
            return

        fishing_event.init()
        skip_count = 0
        while self.state == 1 and WindowClient.running():
            capture = self.window.processed_image(func=image_pre_process)

            # if window server crashed
            if not capture:
                logging.error("Couldn't capture window stopping engine")
                self.turn_off()
                continue

            # crop qr and get the values from it
            values = get_values_from_image(capture)
            # if fishyqr fails to get read multiple times, stop the bot
            if not values:
                skip_count += 1
                logging.error(f"Couldn't read values from FishyQR, skipping {skip_count}/5")
                if skip_count >= 5:
                    logging.error("Stopping engine...")
                    self.turn_off()
                    continue
            else:
                skip_count = 0

            if values:
                fishing_mode.loop(values[3])
            time.sleep(0.1)

        logging.info("Fishing engine stopped")
        fishing_event.unsubscribe()

    def _wait_and_check(self):
        time.sleep(10)
        if not FishEvent.FishingStarted and self.state == 1:
            logging.warning("Doesn't look like fishing has started \n"
                            "Check out #faqs on our discord channel to troubleshoot the issue")

    # TODO: remove this, no longer needed
    def show_pixel_vals(self):
        def show():
            freq = 0.5
            t = 0
            while t < 10.0:
                t += freq
                logging.debug(str(FishingMode.CurrentMode) + ":" + str(self.window.get_capture()[0][0]))
                time.sleep(freq)

        logging.debug("Will display pixel values for 10 seconds")
        time.sleep(5)
        Thread(target=show, args=()).start()


if __name__ == '__main__':
    logging.getLogger("").setLevel(logging.DEBUG)
    # noinspection PyTypeChecker
    fisher = SemiFisherEngine(None)
    fisher.toggle_start()
